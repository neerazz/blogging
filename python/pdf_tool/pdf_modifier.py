import fitz


def process_pdf(input_pdf, output_pdf, header_image_path, footer_text,
                border_style="simple", border_color=(0, 0, 0), border_width=2,
                exclude_top=60, exclude_bottom=40, border_margin=20, rounded_radius=0.1):
    """
    Processes the PDF by:
    - Adding a header image (top-right)
    - Adding a header text (top-left)
    - Adding a page number at bottom-right
    - Drawing a border with a given margin, style, and color
    - Clipping out exclude_top and exclude_bottom from the original PDF
    """

    original_pdf = fitz.open(input_pdf)
    new_pdf = fitz.open()

    for page_num in range(len(original_pdf)):
        original_page = original_pdf.load_page(page_num)
        rect = original_page.rect

        # Create a new page with the same dimensions as the original
        new_page = new_pdf.new_page(width=rect.width, height=rect.height)

        # --------------------------------------------------
        # 1) Insert the original PDF content
        #    Now we shift left and right by border_margin
        #    so that it remains inside the drawn border.
        # --------------------------------------------------
        new_page.show_pdf_page(
            rect=fitz.Rect(border_margin, exclude_top,
                           rect.width - border_margin, rect.height - exclude_bottom),
            src=original_pdf,
            pno=page_num,
            clip=fitz.Rect(border_margin, exclude_top,
                           rect.width - border_margin, rect.height - exclude_bottom)
        )

        # --------------------------------------------------
        # 2) Insert the header image at the top-right
        # --------------------------------------------------
        header_img = fitz.Pixmap(header_image_path)
        header_img_height = 50
        # Scale width proportionally
        header_img_width = header_img.width * (header_img_height / header_img.height)

        # Position: top-right, with ~10px from right edge
        right_margin = 10
        top_margin = 10
        header_img_rect = fitz.Rect(
            rect.width - header_img_width - right_margin,  # left
            top_margin,  # top
            rect.width - right_margin,  # right
            top_margin + header_img_height  # bottom
        )
        new_page.insert_image(header_img_rect, filename=header_image_path)

        # --------------------------------------------------
        # 3) Insert the header text "@BRAINOSAURUS" at top-left
        # --------------------------------------------------
        header_font_size = 12
        header_text_x = 15  # 15px from left
        header_text_y = 25  # 25px from top
        new_page.insert_text(
            fitz.Point(header_text_x, header_text_y),
            footer_text,  # using the same footer_text variable
            fontsize=header_font_size,
            fontname="helv"
        )

        # --------------------------------------------------
        # 4) Insert the page number at the bottom-right
        # --------------------------------------------------
        footer_font_size = 12
        page_number_text = str(page_num + 1)
        page_number_width = fitz.get_text_length(page_number_text,
                                                 fontsize=footer_font_size,
                                                 fontname="helv")
        # Position: about 25px above bottom, 20px from right
        footer_y_position = rect.height - 25
        new_page.insert_text(
            fitz.Point(rect.width - page_number_width - 20, footer_y_position),
            page_number_text,
            fontsize=footer_font_size,
            fontname="helv"
        )

        # --------------------------------------------------
        # 5) Draw the border around the page
        #    Increase border_margin to move it in from the edges
        # --------------------------------------------------
        border_rect = fitz.Rect(
            border_margin, border_margin,
            rect.width - border_margin, rect.height - border_margin
        )

        # Calculate the maximum allowed radius for rounded corners
        max_allowed_radius = min(border_rect.width / 2, border_rect.height / 2)
        # Convert the percentage radius to an absolute value
        radius_value = min(rounded_radius * min(border_rect.width, border_rect.height),
                           max_allowed_radius)

        # Normalize color if needed
        if any(c > 1 for c in border_color):
            border_color = tuple(c / 255 for c in border_color)

        # Choose border style
        if border_style.lower() == "simple":
            new_page.draw_rect(border_rect, color=border_color, width=border_width)
        elif border_style.lower() == "rounded":
            new_page.draw_rect(border_rect, color=border_color, width=border_width,
                               radius=radius_value)
        elif border_style.lower() == "dotted":
            new_page.draw_rect(border_rect, color=border_color, width=border_width,
                               dashes="[1 1] 0")
        else:
            raise ValueError("Unsupported border style. Choose from: 'simple', 'rounded', or 'dotted'.")

    new_pdf.save(output_pdf)


def adjust_pdf_layout(input_pdf, output_pdf, shift_up=20, side_margin=10):
    """
    Adjusts the layout of a PDF by shifting its content up and
    compressing the left and right margins.

    :param input_pdf: Path to the input PDF.
    :param output_pdf: Path to the output PDF.
    :param shift_up: How many pixels to move the PDF content up.
    :param side_margin: How many pixels to trim from the left and right sides.
    """
    doc = fitz.open(input_pdf)
    new_doc = fitz.open()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        rect = page.rect  # Original page size (width, height)

        # Create a new blank page with the same dimensions
        new_page = new_doc.new_page(width=rect.width, height=rect.height)

        # Show the original page content on the new page:
        # - We shrink from left & right by side_margin
        # - We shift upward by shift_up
        new_page.show_pdf_page(
            rect=fitz.Rect(side_margin, -shift_up,
                           rect.width - side_margin, rect.height - shift_up),
            src=doc,
            pno=page_num
        )

    new_doc.save(output_pdf)
    print(f"PDF layout adjusted and saved as: {output_pdf}")


if __name__ == "__main__":
    input_pdf = "../../input.pdf"
    output_pdf = "../../output.pdf"
    header_image_path = "../../resources/brand_logo.png"  # Update path as needed

    # Text to place at the top-left
    footer_text = "@BRAINOSAURUS"

    # Adjust these as desired
    exclude_top = 60
    exclude_bottom = 40

    # Choose from style: "simple", "rounded", "dotted"
    border_style = "simple"

    # Increase this margin to bring the border further from the edges
    # and keep the content within the dotted lines
    border_margin = 20

    # Example border color (a light "sky blue")
    border_color = (135 / 255, 206 / 255, 235 / 255)

    # process_pdf(
    #     input_pdf,
    #     output_pdf,
    #     header_image_path,
    #     footer_text,
    #     border_style=border_style,
    #     border_color=border_color,
    #     exclude_top=exclude_top,
    #     exclude_bottom=exclude_bottom,
    #     border_margin=border_margin
    # )

    adjust_pdf_layout(input_pdf, output_pdf,
                      shift_up=30,  # Move content 20px upwards
                      side_margin=18  # Compress 10px from left/right
                      )

    print(f"PDF saved successfully as {output_pdf}")
