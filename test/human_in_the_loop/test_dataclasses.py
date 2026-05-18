# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

from haystack.human_in_the_loop import ConfirmationUIResult, ToolExecutionDecision


class TestConfirmationUIResult:
    def test_init(self):
        original = ConfirmationUIResult(action="reject", feedback="Changed my mind")
        assert original.action == "reject"
        assert original.feedback == "Changed my mind"
        assert original.new_tool_params is None
        assert original.resolved_status() == "rejected"

    def test_resolved_status_from_explicit_status(self):
        original = ConfirmationUIResult(action="custom", status="modified")
        assert original.resolved_status() == "modified"


class TestToolExecutionDecision:
    def test_init(self):
        decision = ToolExecutionDecision(
            execute=True,
            tool_name="test_tool",
            tool_call_id="test_tool_call_id",
            final_tool_params={"param1": "new_value"},
        )
        assert decision.execute is True
        assert decision.final_tool_params == {"param1": "new_value"}
        assert decision.tool_call_id == "test_tool_call_id"
        assert decision.tool_name == "test_tool"
        assert decision.status == "approved"

    def test_to_dict(self):
        original = ToolExecutionDecision(
            execute=True,
            tool_name="test_tool",
            tool_call_id="test_tool_call_id",
            final_tool_params={"param1": "new_value"},
        )
        as_dict = original.to_dict()
        assert as_dict == {
            "execute": True,
            "tool_name": "test_tool",
            "tool_call_id": "test_tool_call_id",
            "feedback": None,
            "final_tool_params": {"param1": "new_value"},
            "status": "approved",
        }

    def test_from_dict(self):
        data = {
            "execute": False,
            "tool_name": "another_tool",
            "tool_call_id": "another_tool_call_id",
            "feedback": "Not needed",
            "final_tool_params": {"paramA": 123},
        }
        decision = ToolExecutionDecision.from_dict(data)
        assert decision.execute is False
        assert decision.tool_name == "another_tool"
        assert decision.tool_call_id == "another_tool_call_id"
        assert decision.feedback == "Not needed"
        assert decision.final_tool_params == {"paramA": 123}
        assert decision.status == "rejected"

    def test_from_dict_legacy_payload_without_status(self):
        data = {
            "execute": True,
            "tool_name": "legacy_tool",
            "tool_call_id": "legacy-tool-call-id",
            "feedback": "The parameters for tool 'legacy_tool' were updated by the user to:\n{'x': 2}",
            "final_tool_params": {"x": 2},
        }
        decision = ToolExecutionDecision.from_dict(data)
        assert decision.execute is True
        assert decision.status == "modified"
