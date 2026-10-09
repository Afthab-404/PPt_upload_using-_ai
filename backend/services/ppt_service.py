from pptx import Presentation
import os
from pptx.util import Pt
from pptx.util import Inches, Pt


def create_ppt(slides, filename, template_path=None, presentation_title=None):
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)

    if template_path and os.path.exists(template_path):
        prs = Presentation(template_path)
    else:
        prs = Presentation()

    if not slides:
        raise ValueError("No slide content was provided.")

    presentation_title = presentation_title or slides[0].get(
        "title", "Presentation"
    )

    # Reuse existing template slides first.
    # Add blank-layout slides if the generated content needs more slides.
    while len(prs.slides) < len(slides):
        prs.slides.add_slide(prs.slide_layouts[1])

    for index, slide_data in enumerate(slides):
        slide = prs.slides[index]
        title = str(slide_data.get("title", ""))
        content = slide_data.get("content", [])

        # Identify the existing footer and update its text separately.
        footer_shapes = []
        content_shapes = []

        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue

            existing_text = shape.text.strip()

            if existing_text == "Flutter Project Flow":
                footer_shapes.append(shape)
            elif existing_text:
                content_shapes.append(shape)

        # Prefer an existing title placeholder when one is available.
        title_shape = None

        for shape in content_shapes:
            if shape.is_placeholder:
                placeholder_type = shape.placeholder_format.type
                if str(placeholder_type) == "TITLE (1)":
                    title_shape = shape
                    break

        # Otherwise, use the largest existing content text box.
        if title_shape is None and content_shapes:
            title_shape = max(
                content_shapes,
                key=lambda shape: shape.width * shape.height
            )

        if title_shape is not None:
            text_frame = title_shape.text_frame
            text_frame.clear()

            paragraph = text_frame.paragraphs[0]
            paragraph.text = title
            paragraph.font.bold = True
            paragraph.font.size = Pt(24)

            for point in content:
                paragraph = text_frame.add_paragraph()
                paragraph.text = f"• {point}"
                paragraph.level = 0
                paragraph.font.size = Pt(16)

        # Clear other old content boxes so the original Flutter text
        # does not remain alongside the new AI-generated content.
        for shape in content_shapes:
            if shape is title_shape:
                continue

            shape.text_frame.clear()

        # Replace the old topic footer while retaining its position.
        for shape in footer_shapes:
            shape.text = presentation_title

    prs.save(filename)

    return filename
