import pdfplumber

with pdfplumber.open("docs/PO.PDF") as pdf:
  im = pdf.pages[0].to_image(resolution=150)
  words = pdf.pages[0].extract_words(
    use_text_flow=False,
    x_tolerance=10,
  )
  print(pdf.pages[0].extract_text())
  # im.draw_rects(words)
  # im.save("docs/PO.png", format="PNG")

    # for page in pdf.pages:
    #     print(page.extract_text())
        # words = page.extract_words(x_tolerance=3, y_tolerance=3, keep_blank_chars=False, use_text_flow=False, horizontal_ltr=True, vertical_ttb=True, extra_attrs=[], split_at_punctuation=False, expand_ligatures=True)
        # print(words)
        # tables = page.extract_tables()
        # if tables:
        #     for table in tables:
        #         # 输出表格内容
        #         for row in table:
        #             print(111111111)
        #             print(row)