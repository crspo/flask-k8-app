def generate_img_html(base64_str: str) -> str:
  """
    Creates an HTML <img> tag using a Base64-encoded image.

    Args:
        base64_str (str): Encoded image string.

    Returns:
        str: HTML image tag for rendering in browser.
  """
  return f'<img src="data:image/png;base64,{base64_str}"/>'

def generate_print_script() -> str:
  """
    Returns JavaScript code for printing the QR image in a pop-up window.

    Uses window.open to isolate the image and launch the browser print dialog.

    Returns:
        str: JavaScript block for embedding in HTML.
  """
  return '''
    <script>
      function printQRCode() {
        const printWindow = window.open('', '', 'height=600,width=800');
        printWindow.document.write('<html><head><title>Print QR Code</title></head><body>');
        printWindow.document.write(document.querySelector('img').outerHTML);
        printWindow.document.write('</body></html>');
        printWindow.document.close();
        printWindow.focus();
        printWindow.print();
        printWindow.close();
      }
    </script>
    '''
