# Tg_bot_Yandex_OCR
Telegram bot for recognizing handwritten questionnaires.\
The text recognition module - Yandex OCR.\
The bot accepts a PDF or an image with scanned questionnaires as input, then, if a PDF is received, it is divided into separate image files using the Fitz library.
After splitting the files into images, using OpenCV tools, we align the image to the middle corner of straight lines so that the text becomes horizontal. This makes it easier to further parse the recognized text by coordinates and form a summary table with the results.\
The result of the Yandex OCR recognition module is presented in a structured JSON format, which is further parsed into a list of recognized words with coordinates.\
Next, a list of keys with coordinates is formed from the list, by comparison with the available questionnaire fields from the field_list list. The comparison is performed by pairwise matching of recognized words to find the full occurrence of the string in the key string. This way, only those fields of the questionnaire that were in the recognized image are found.\
After forming a list of recognized fields, the boundaries of the end of the segment in which the handwritten text is located are determined. This is necessary to accurately capture only handwritten text, since two fields can be on the same line. The segment boundary is determined by comparing the X coordinates of the found keys located at the same Y coordinate.
When the keys with the coordinates and boundaries of the search segments are formed, we search for the recognized handwritten text by entering the ranges and write it into the resulting dataframe.\
The bot sends an Excel file to the telegram output, ready for validation and export to the CRM system.

