from pptx import Presentation
import os

def create_ppt(slides, filename):

    os.makedirs("presentations", exist_ok=True)

    prs = Presentation()

    for slide_data in slides:

        slide = prs.slides.add_slide(
            prs.slide_layouts[1]
        )

        slide.shapes.title.text = slide_data["title"]

        slide.placeholders[1].text = "\n".join(
            slide_data["content"]
        )

    prs.save(filename)