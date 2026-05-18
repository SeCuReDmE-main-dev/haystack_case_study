# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

from dataclasses import asdict, dataclass
from typing import Any, Literal

DecisionStatus = Literal["approved", "modified", "rejected"]


@dataclass
class ConfirmationUIResult:
    """
    Result of the confirmation UI interaction.

    :param action:
        The action taken by the user such as "confirm", "reject", or "modify".
        This action type is not enforced to allow for custom actions to be implemented.
    :param feedback:
        Optional feedback message from the user. For example, if the user rejects the tool execution,
        they might provide a reason for the rejection.
    :param new_tool_params:
        Optional set of new parameters for the tool. For example, if the user chooses to modify the tool parameters,
        they can provide a new set of parameters here.
    :param status:
        Optional explicit decision status. When omitted, built-in actions are normalized as:
        `confirm` -> `approved`, `modify` -> `modified`, `reject` -> `rejected`.
    """

    action: str  # "confirm", "reject", "modify"
    feedback: str | None = None
    new_tool_params: dict[str, Any] | None = None
    status: DecisionStatus | None = None

    def resolved_status(self) -> DecisionStatus:
        """
        Resolve the explicit decision status for this UI result.

        :raises ValueError:
            If neither a supported built-in action nor an explicit status is provided.
        """
        if self.status is not None:
            return self.status

        if self.action == "confirm":
            return "approved"
        if self.action == "modify":
            return "modified"
        if self.action == "reject":
            return "rejected"

        raise ValueError(
            "Unsupported confirmation action. Provide one of 'confirm', 'modify', 'reject' or set 'status' explicitly."
        )


@dataclass
class ToolExecutionDecision:
    """
    Decision made regarding tool execution.

    :param tool_name:
        The name of the tool to be executed.
    :param execute:
        A boolean indicating whether to execute the tool with the provided parameters.
    :param tool_call_id:
        Optional unique identifier for the tool call. This can be used to track and correlate the decision with a
        specific tool invocation.
    :param feedback:
        Optional feedback message.
        For example, if the tool execution is rejected, this can contain the reason. Or if the tool parameters were
        modified, this can contain the modification details.
    :param final_tool_params:
        Optional final parameters for the tool if execution is confirmed or modified.
    :param status:
        Explicit decision status. When omitted, it is inferred from the legacy `execute`/`feedback` shape to remain
        backward-compatible with older serialized payloads.
    """

    tool_name: str
    execute: bool
    tool_call_id: str | None = None
    feedback: str | None = None
    final_tool_params: dict[str, Any] | None = None
    status: DecisionStatus | None = None

    def __post_init__(self) -> None:
        if self.status is None:
            self.status = self._infer_status()
        else:
            self.execute = self.status != "rejected"

    def _infer_status(self) -> DecisionStatus:
        if not self.execute:
            return "rejected"
        if self.feedback is not None and self.final_tool_params is not None:
            return "modified"
        return "approved"

    def resolved_status(self) -> DecisionStatus:
        """
        Return the normalized decision status for this execution decision.
        """
        return self.status

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the ToolExecutionDecision to a dictionary representation.

        :return: A dictionary containing the tool execution decision details.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolExecutionDecision":
        """
        Populate the ToolExecutionDecision from a dictionary representation.

        :param data: A dictionary containing the tool execution decision details.
        :return: An instance of ToolExecutionDecision.
        """
        return cls(**data)
