"""Metric configuration that keeps RAGAS aligned with medical RAG behavior."""

from __future__ import annotations


def build_medical_answer_relevancy_metric():
    """Create Answer Relevancy with a Chinese medical noncommittal definition.

    RAGAS 0.2.15 uses a default English prompt. Its score becomes zero when any
    generated question labels a response as noncommittal. Medical safety language
    such as "仅供参考" was therefore masking otherwise direct answers. The metric
    still measures the original Answer Relevancy algorithm; only that binary
    classification is calibrated to the product's required safety boundary.
    """
    from ragas.metrics import AnswerRelevancy
    from ragas.metrics._answer_relevance import (
        ResponseRelevanceInput,
        ResponseRelevanceOutput,
    )
    from ragas.prompt import PydanticPrompt

    class ChineseMedicalResponseRelevancePrompt(
        PydanticPrompt[ResponseRelevanceInput, ResponseRelevanceOutput]
    ):
        instruction = """你正在评估医疗健康知识库回答的相关性。
根据“回答”生成一个该回答能够直接解答的中文问题，并判断回答是否属于回避。

只有在回答没有提供任何与用户问题有关的信息、只说“不知道”、只说“资料不足”、
只说“请咨询医生”，或明显答非所问时，才将 noncommittal 设为 1。
以下情况必须设为 0：回答已经给出资料内容、药物信息、资料标题、专科名称、
明确的就医建议或警示信号，即使结尾同时出现“仅供参考”“不代替医生诊断”
“建议就医”等医疗安全提示。

对“哪份资料”“哪个专科”“看什么说明”一类问题，只要回答明确给出资料标题、
专科或说明，即视为直接回答，不得判为回避。
生成的问题应保持回答的语言和具体程度，不要翻译成英文，也不要扩展回答没有涉及的内容。"""
        input_model = ResponseRelevanceInput
        output_model = ResponseRelevanceOutput
        examples = [
            (
                ResponseRelevanceInput(
                    response=(
                        "建议优先查看《焦虑障碍健康知识》资料。资料介绍了焦虑"
                        "影响日常生活时可咨询专业人员。内容仅供健康信息参考。"
                    )
                ),
                ResponseRelevanceOutput(
                    question="焦虑影响日常生活时应查看哪份资料？",
                    noncommittal=0,
                ),
            ),
            (
                ResponseRelevanceInput(
                    response=(
                        "资料提示出现持续胸痛或呼吸困难时，应立即寻求紧急医疗帮助。"
                        "内容仅供健康信息参考，不代替医生诊断。"
                    )
                ),
                ResponseRelevanceOutput(
                    question="出现持续胸痛或呼吸困难时应如何处理？",
                    noncommittal=0,
                ),
            ),
            (
                ResponseRelevanceInput(
                    response="我不知道，建议咨询医生。"
                ),
                ResponseRelevanceOutput(question="", noncommittal=1),
            ),
        ]

    return AnswerRelevancy(
        question_generation=ChineseMedicalResponseRelevancePrompt()
    )
