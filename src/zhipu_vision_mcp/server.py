"""
智谱视觉理解 MCP Server
对标 zai-mcp-server 的 8 个视觉工具，调用智谱 API（GLM-4.6V / GLM-5V-Turbo）
"""

import os
import base64
from zhipuai import ZhipuAI
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("zhipu-vision")

MIME_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".m4v": "video/mp4",
}


def get_client() -> ZhipuAI:
    return ZhipuAI(api_key=os.environ["ZHIPUAI_API_KEY"])


def encode_file(path: str) -> tuple[str, str]:
    ext = os.path.splitext(path)[1].lower()
    mime = MIME_MAP.get(ext, "image/jpeg")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return b64, mime


def build_image_content(source: str) -> dict:
    if source.startswith(("http://", "https://")):
        return {"type": "image_url", "image_url": {"url": source}}
    b64, mime = encode_file(source)
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}


def call_vision(model: str, content_list: list, prompt: str, thinking: bool = True) -> str:
    client = get_client()
    messages = [{"role": "user", "content": content_list + [{"type": "text", "text": prompt}]}]
    kwargs = {
        "model": model,
        "messages": messages,
        "stream": False,
        "max_tokens": 65536 if model == "glm-5v-turbo" else 16384,
    }
    if thinking:
        kwargs["thinking"] = {"type": "enabled"}
    response = client.chat.completions.create(**kwargs)
    msg = response.choices[0].message
    result = ""
    if hasattr(msg, "reasoning_content") and msg.reasoning_content:
        result += f"【思考过程】\n{msg.reasoning_content}\n\n"
    result += msg.content
    return result


# ─── Tool 1: analyze_image ───────────────────────────────────────────


@mcp.tool()
def analyze_image(image_source: str, prompt: str, model: str = "glm-4.6v") -> str:
    """通用图像分析。支持本地路径或 URL。

    Args:
        image_source: 图片路径或 URL
        prompt: 分析要求
        model: 模型名称，默认 glm-4.6v
    """
    content = [build_image_content(image_source)]
    return call_vision(model, content, prompt)


# ─── Tool 2: analyze_video ───────────────────────────────────────────


@mcp.tool()
def analyze_video(video_source: str, prompt: str, model: str = "glm-4.6v") -> str:
    """视频内容分析。支持本地视频路径或 URL。

    Args:
        video_source: 视频路径或 URL
        prompt: 分析要求
        model: 模型名称，默认 glm-4.6v
    """
    content = [build_image_content(video_source)]
    return call_vision(model, content, prompt)


# ─── Tool 3: analyze_data_visualization ───────────────────────────────


@mcp.tool()
def analyze_data_visualization(
    image_source: str,
    prompt: str,
    analysis_focus: str = "",
) -> str:
    """分析数据可视化图表，提取数据趋势、异常点和关键指标。

    Args:
        image_source: 图表截图路径或 URL
        prompt: 分析要求
        analysis_focus: 可选聚焦方向：trends/anomalies/comparisons/performance metrics
    """
    system = (
        "你是一位数据可视化分析专家。请分析提供的图表/数据可视化图像，要求：\n"
        "1. 识别图表类型和展示的核心数据\n"
        "2. 提取关键数值和趋势\n"
        "3. 标注异常点和数据拐点\n"
        "4. 对比不同数据系列的差异\n"
        "5. 给出基于数据的结论和建议"
    )
    if analysis_focus:
        system += f"\n\n请特别关注：{analysis_focus}"
    full_prompt = system + "\n\n用户补充要求：" + prompt
    content = [build_image_content(image_source)]
    return call_vision("glm-4.6v", content, full_prompt)


# ─── Tool 4: diagnose_error_screenshot ───────────────────────────────


@mcp.tool()
def diagnose_error_screenshot(
    image_source: str,
    prompt: str,
    context: str = "",
) -> str:
    """诊断错误截图，识别错误类型并给出修复建议。

    Args:
        image_source: 错误截图路径或 URL
        prompt: 诊断要求
        context: 可选，错误发生时的场景描述（如"npm install 时"或"部署后"）
    """
    system = (
        "你是一位资深全栈工程师，擅长诊断各类错误。请分析错误截图，要求：\n"
        "1. 识别错误类型（编译错误/运行时错误/网络错误/权限错误等）\n"
        "2. 提取关键错误信息（错误码、堆栈跟踪、文件路径等）\n"
        "3. 分析根本原因\n"
        "4. 给出具体修复步骤\n"
        "5. 提供预防类似错误的建议"
    )
    if context:
        system += f"\n\n错误发生场景：{context}"
    full_prompt = system + "\n\n用户补充要求：" + prompt
    content = [build_image_content(image_source)]
    return call_vision("glm-4.6v", content, full_prompt)


# ─── Tool 5: extract_text_from_screenshot ─────────────────────────────


@mcp.tool()
def extract_text_from_screenshot(
    image_source: str,
    prompt: str,
    programming_language: str = "",
) -> str:
    """从截图中提取文字（OCR），支持代码和文档识别。

    Args:
        image_source: 截图路径或 URL
        prompt: 提取要求
        programming_language: 可选，截图包含的编程语言（如 python/javascript）
    """
    system = (
        "你是一位 OCR 专家，请精确提取截图中的所有文字内容，要求：\n"
        "1. 完整转录所有可见文字，不遗漏\n"
        "2. 保持原文的格式和层级结构\n"
        "3. 如果是代码，保持缩进和语法格式\n"
        "4. 如果文字模糊或有歧义，标注 [不确定]"
    )
    if programming_language:
        system += f"\n\n截图中的编程语言：{programming_language}"
    full_prompt = system + "\n\n用户补充要求：" + prompt
    content = [build_image_content(image_source)]
    return call_vision("glm-4.6v", content, full_prompt)


# ─── Tool 6: ui_to_artifact ──────────────────────────────────────────


@mcp.tool()
def ui_to_artifact(
    image_source: str,
    output_type: str,
    prompt: str,
) -> str:
    """将 UI 截图转换为代码、设计规范、AI 提示词或自然语言描述。

    Args:
        image_source: UI 截图路径或 URL
        output_type: 输出类型 — code（前端代码）/ prompt（AI 提示词）/ spec（设计规范）/ description（自然语言描述）
        prompt: 补充指令
    """
    output_instructions = {
        "code": (
            "请根据设计稿生成完整可运行的前端代码。要求：\n"
            "1. 使用 HTML + CSS + JavaScript，单文件完整实现\n"
            "2. 精确还原设计稿的布局、颜色、字体、间距\n"
            "3. 使用语义化标签和响应式设计\n"
            "4. 代码整洁、有适当注释\n"
            "5. 所有交互元素可用"
        ),
        "prompt": (
            "请根据 UI 设计稿生成一段详细的 AI 提示词，用于指导 AI 重新生成该界面。要求：\n"
            "1. 描述整体布局和组件层级\n"
            "2. 列出所有颜色值（背景、文字、边框等）\n"
            "3. 说明字体大小、粗细和间距\n"
            "4. 描述交互状态和动画效果"
        ),
        "spec": (
            "请提取 UI 设计稿的设计规范文档。要求：\n"
            "1. 颜色体系：主色、辅色、背景色、文字色，标注 HEX 值\n"
            "2. 字体体系：字体族、大小层级、粗细\n"
            "3. 间距体系：内边距、外边距、元素间距\n"
            "4. 组件规范：按钮、卡片、表单等尺寸和样式\n"
            "5. 圆角、阴影等装饰参数"
        ),
        "description": (
            "请用自然语言详细描述该 UI 界面，要求：\n"
            "1. 从上到下描述整体布局\n"
            "2. 描述每个组件的外观和功能\n"
            "3. 说明视觉层级和阅读流\n"
            "4. 总结设计风格和用户体验特征"
        ),
    }
    instruction = output_instructions.get(output_type, output_instructions["description"])
    full_prompt = instruction + "\n\n用户补充要求：" + prompt
    content = [build_image_content(image_source)]
    return call_vision("glm-5v-turbo", content, full_prompt)


# ─── Tool 7: ui_diff_check ──────────────────────────────────────────


@mcp.tool()
def ui_diff_check(
    expected_image_source: str,
    actual_image_source: str,
    prompt: str,
) -> str:
    """对比设计稿与实际实现，逐维度输出差异清单。

    Args:
        expected_image_source: 设计稿/预期图路径或 URL
        actual_image_source: 实际实现截图路径或 URL
        prompt: 对比要求
    """
    system = (
        "你是一位 UI 质检专家。请对比两张图片（第一张是设计稿/预期效果，第二张是实际实现），"
        "逐维度分析差异：\n"
        "1. 布局差异：组件位置、对齐方式、层级关系\n"
        "2. 颜色差异：背景色、文字色、边框色等\n"
        "3. 字体差异：字体族、大小、粗细\n"
        "4. 间距差异：内边距、外边距、元素间距\n"
        "5. 组件差异：缺失/多余/变形的组件\n"
        "6. 图片/图标差异：尺寸、位置、样式\n\n"
        "输出格式：按维度列出差异，每项标注严重程度（高/中/低），并给出修复建议。"
    )
    full_prompt = system + "\n\n用户补充要求：" + prompt
    content = [
        build_image_content(expected_image_source),
        build_image_content(actual_image_source),
    ]
    return call_vision("glm-4.6v", content, full_prompt)


# ─── Tool 8: understand_technical_diagram ────────────────────────────


@mcp.tool()
def understand_technical_diagram(
    image_source: str,
    prompt: str,
    diagram_type: str = "",
) -> str:
    """理解和解析技术图表（架构图、流程图、UML、ER 图等）。

    Args:
        image_source: 图表路径或 URL
        prompt: 分析要求
        diagram_type: 可选图表类型 — architecture/flowchart/uml/er-diagram/sequence
    """
    type_hints = {
        "architecture": "系统架构图：识别各服务/模块、通信方式、数据流向、部署拓扑",
        "flowchart": "流程图：跟踪决策分支、循环、并行路径，识别关键判断节点",
        "uml": "UML 图：解析类关系（继承/组合/依赖）、方法签名、访问修饰符",
        "er-diagram": "ER 图：识别实体、属性、关系类型（1:1/1:N/M:N）、主外键",
        "sequence": "时序图：跟踪消息传递顺序、同步/异步调用、参与者角色",
    }
    system = "你是一位技术文档分析专家。请解析提供的技术图表，要求：\n"
    if diagram_type and diagram_type in type_hints:
        system += f"\n图表类型：{type_hints[diagram_type]}\n"
    system += (
        "\n1. 识别图中的所有组件/实体/节点\n"
        "2. 解析组件之间的关系和数据流向\n"
        "3. 提取关键标注、注释和说明文字\n"
        "4. 还原图表表达的完整逻辑或架构\n"
        "5. 用结构化文字重新描述图表内容"
    )
    full_prompt = system + "\n\n用户补充要求：" + prompt
    content = [build_image_content(image_source)]
    return call_vision("glm-4.6v", content, full_prompt)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
