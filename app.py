# from flask import Flask, flash, request, jsonify, send_file,send_from_directory, url_for
# import os
# import subprocess
# from concurrent.futures import ThreadPoolExecutor
# from datetime import datetime
# from pathlib import Path
# from PIL import Image
# from fpdf import FPDF
# from openai import OpenAI
# from dotenv import load_dotenv
# from flask_cors import CORS
# from werkzeug.utils import secure_filename
# from rembg import remove  # Ensure you have this import at the top

# load_dotenv()




# ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif',
#                           'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'csv', 'zip', 'rar', 'mp4',
#                           'mp3', 'wav', 'avi', 'mkv', 'flv', 'mov', 'wmv'])

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "http://localhost:3000", "methods": ["GET", "POST", "OPTIONS"]}})
# app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.dirname(__file__)) + '/Downloads/'  # Set UPLOAD_FOLDER in config
# UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']

# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
# # Load the SYSTEM_PROMPT from an external file
# try:
#     with open("ycai_prompt.txt", "r") as file:
#         SYSTEM_PROMPT = file.read()
# except FileNotFoundError:
#     print("ycai_prompt.txt not found. Using default prompt.")
#     SYSTEM_PROMPT = "Default prompt here"
    
# @app.before_request
# def log_request_info():
#     print(f"Request Method: {request.method}")
#     print(f"Request URL: {request.url}")
#     # print(f"Request Headers: {request.headers}")       
    
# @app.route('/chat', methods=['GET', 'POST'])
# def chat():

#     print("Request data:", request.get_data(as_text=True))
    
#     if request.method == 'GET':
#         return jsonify({"message": "Hello from Flask!"}), 200
    
#     if request.method == 'POST':
#         try:
#             data = request.get_json(force=True)
#             print("Parsed JSON data:", data)
            
#             if not data:
#                 return jsonify({"error": "No JSON data provided"}), 400

#             message = data.get("message", "")
#             user_id = data.get("userId", "")
#             conversation_id = data.get("conversationId", "")

#             # Call OpenAI API
#             response = client.chat.completions.create(
#                 model="gpt-4",  # or "gpt-3.5-turbo" depending on your preference
#                 messages=[
#                     {"role": "system", "content": SYSTEM_PROMPT},
#                     {"role": "user", "content": message}
#                 ],
#             )

#             ai_response = response.choices[0].message.content
#             print(ai_response)

#             return jsonify({
#                 "response": ai_response,
#                 "userId": user_id,
#                 "conversationId": conversation_id
#             }), 200

#         except Exception as e:
#             print(f"Error processing POST request: {str(e)}")
#             return jsonify({"error": str(e)}), 500

#     return jsonify({"error": "Method not allowed"}), 405

# # Function to convert an image to black and white
# def convert_to_black_and_white(image):
#     grayscale_image = image.convert('L')
#     threshold = 128  # Adjust this threshold as needed
#     bw_image = grayscale_image.point(lambda p: p > threshold and 255)
#     return bw_image

# # Function to convert JPG to SVG and upscale
# def jpg_to_svg_and_upscale(jpg_filepath, output_dir):
#     svg_filename = f"{Path(jpg_filepath).stem}.svg"
#     svg_filepath = os.path.join(output_dir, svg_filename)

#     # Open and convert the JPG image to black and white
#     with Image.open(jpg_filepath) as img:
#         bw_image = convert_to_black_and_white(img)
#         pbm_filepath = jpg_filepath.rsplit('.', 1)[0] + '.pbm'
#         bw_image.save(pbm_filepath)

#     # Ensure the output directory exists
#     os.makedirs(output_dir, exist_ok=True)

#     try:
#         # Use potrace to convert the PBM to SVG
#         subprocess.run(['potrace', '-s', pbm_filepath, '-o', svg_filepath], check=True)
#         os.remove(pbm_filepath)  # Remove the temporary PBM file
#         return svg_filepath
#     except subprocess.CalledProcessError as e:
#         print(f"Potrace returned a non-zero exit status: {e}")
#         return None

# # Function to sanitize text
# def sanitize_text(text):
#     replacements = {
#         '\u201c': '"', '\u201d': '"',
#         '\u2018': "'", '\u2019': "'",
#         '\u2013': '-', '\u2014': '-',
#         # Add more replacements as needed
#     }
#     for original, replacement in replacements.items():
#         text = text.replace(original, replacement)
#     return text

# # Function to generate a PDF from content
# def generate_pdf(content, filename, background_image=None, logo_image=None):
#     pdf = PDF()

#     # Set background and logo if provided
#     pdf.background_image = background_image
#     pdf.logo_image = logo_image

#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
#     pdf.set_auto_page_break(auto=True, margin=15)

#     lines = content.split('\n')
#     for line in lines:
#         line = sanitize_text(line)
#         if pdf.get_y() > 240:
#             pdf.add_page()
#         if "**" in line:
#             line = line.replace("**", "")
#             pdf.set_font("Arial", style='B', size=12)
#             pdf.multi_cell(0, 10, txt=line, align="L")
#             pdf.set_font("Arial", size=12)
#         else:
#             pdf.multi_cell(0, 10, txt=line, align="L")

#     # Save the PDF to the specified filename
#     pdf.output(filename)

# # Define the PDF class
# class PDF(FPDF):
#     def __init__(self, orientation='P', unit='mm', format='A4'):
#         super().__init__(orientation, unit, format)
#         self.background_image = None
#         self.logo_image = None
#         self.set_left_margin(35)
#         self.set_top_margin(40)
#         self.set_auto_page_break(auto=True, margin=10)

#     def add_page(self, orientation=''):
#         super().add_page(orientation=orientation)
#         if self.background_image:
#             self.image(self.background_image, x=0, y=0, w=self.w, h=self.h)
#         if self.logo_image:
#             # Calculate the logo size and position
#             logo_max_width = 50  # Maximum width for the logo
#             logo_max_height = 50  # Maximum height for the logo

#             with Image.open(self.logo_image) as img:
#                 logo_width, logo_height = img.size
#                 aspect_ratio = logo_width / logo_height

#                 if logo_width > logo_max_width:
#                     logo_width = logo_max_width
#                     logo_height = logo_width / aspect_ratio

#                 if logo_height > logo_max_height:
#                     logo_height = logo_max_height
#                     logo_width = logo_height * aspect_ratio

#                 # Center the logo horizontally and position it
#                 logo_x = (self.w - logo_width) / 2
#                 logo_y = 20  # Adjust this value to bring the logo down or up

#                 self.image(self.logo_image, x=logo_x, y=logo_y, w=logo_width, h=logo_height)

#     def header(self):
#         self.set_y(65)  # Adjust this value to position text under the logo


# # Function to upscale the image
# def upscale_image(image_path, scale_factor):
#     # Open the image file
#     with Image.open(image_path) as img:
#         # Calculate new dimensions
#         new_width = int(img.width * scale_factor)
#         new_height = int(img.height * scale_factor)
        
#         # Resize the image
#         upscaled_image = img.resize((new_width, new_height), Image.LANCZOS)
        
#         # Save the upscaled image to a new file
#         upscaled_image_path = os.path.splitext(image_path)[0] + '_upscaled.png'
#         upscaled_image.save(upscaled_image_path)
        
#         return upscaled_image_path

# # Function to process images (e.g., upscale, remove background)
# @app.route('/process_image', methods=['POST'])
# def process_image():
#     # Step 1: Log the incoming request files
#     print("Request files:", request.files)  
    
#     # Step 2: Ensure an image file is provided
#     if 'file' not in request.files:
#         return jsonify({"error": "No image file provided"}), 400

#     image_file = request.files['file']
#     if image_file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     # Step 3: Define the output directory
#     output_dir = 'outputImages'
#     os.makedirs(output_dir, exist_ok=True)

#     # Step 4: Process the image (e.g., save it)
#     try:
#         # Save the original image to the output directory
#         output_path = os.path.join(output_dir, secure_filename(image_file.filename))
#         image_file.save(output_path)

#         # Step 5: Remove the background from the image
#         with open(output_path, 'rb') as input_file:
#             input_image = input_file.read()
#             output_image = remove(input_image)  # Remove background

#         # Save the processed image with background removed
#         bg_removed_path = os.path.join(output_dir, 'bg_removed_' + secure_filename(image_file.filename))
#         with open(bg_removed_path, 'wb') as output_file:
#             output_file.write(output_image)

#         # Step 6: Upscale the image
#         upscaled_image_path = upscale_image(bg_removed_path, scale_factor=3)  # You can adjust the scale factor

#         # Step 7: Generate the URL to access the upscaled image
#         upscaled_image_url = url_for('display_image', filename=os.path.basename(upscaled_image_path), _external=True)

#         # Step 8: Return the output directory and image URL
#         return jsonify({
#             "message": "Image processed, background removed, and upscaled successfully.",
#             "output_directory": output_dir,
#             "image_url": upscaled_image_url
#         }), 200

#     except Exception as e:
#         print(f"Error processing image: {str(e)}")
#         return jsonify({"error": str(e)}), 500


    
    
    
# @app.route('/vectorize_image', methods=['POST'])
# def vectorize_image():
#     data = request.json
#     image_path = data.get('image_path')
#     output_dir = data.get('output_dir', '/tmp')

#     if not image_path:
#         return jsonify({'error': 'No image_path provided'}), 400

#     svg_file = jpg_to_svg_and_upscale(image_path, output_dir)
#     if svg_file:
#         return send_file(svg_file, as_attachment=True)
#     else:
#         return jsonify({'error': 'Failed to vectorize image'}), 500

# @app.route('/generate_pdf', methods=['POST'])
# def generate_pdf_endpoint():
#     data = request.json
#     print("Parsed JSON data:", data)
#     filename = data.get('filename', 'output.pdf')
#     background_image = data.get('background_image')
#     logo_image = data.get('logo_image')
#     prompt = data.get('content', '')  # Get the content from the request data
    
#     print(f"Filename: {filename}")
#     print(f"Background image: {background_image}")
#     print(f"Logo image: {logo_image}")
#     print(f"Prompt: {prompt}")

#     try:
#         # Generate content using ChatGPT
#         response = client.chat.completions.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant that generates informative content for PDFs."},
#                 {"role": "user", "content": f"Generate content for a PDF on the topic: {prompt}"}
#             ],
#         )
#         content = response.choices[0].message.content

#         # Generate PDF with the content
#         generate_pdf(content, filename, background_image, logo_image)
#         return send_file(filename, as_attachment=True)
#     except Exception as e:
#         print(f"Error during PDF generation: {str(e)}")  # Log the error
#         return jsonify({'error': f'Failed to generate PDF: {str(e)}'}), 500



# def allowedFile(filename):
#        return '.' in filename and \
#               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
# def generate_pdf_from_data(pdf_data):
#     # Specify the directory to save PDFs
#     output_dir = 'pdf_collection'  # Change this to your desired directory
#     os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

#     print("pdf_data:", pdf_data)
#     filename = pdf_data.get('filename', 'output.pdf')
#     background_image = pdf_data.get('background_image')
#     logo_image = pdf_data.get('logo_image')
#     prompt = pdf_data.get('content', '')

#     # Check if the background image is a PNG, JPEG, or JPG file
#     if background_image and not (background_image.lower().endswith('.png') or 
#                                  background_image.lower().endswith('.jpg') or 
#                                  background_image.lower().endswith('.jpeg')):
#         return jsonify({'error': 'Background image must be a PNG, JPEG, or JPG file.'}), 400

#     # Update the filename to include the output directory
#     output_filepath = os.path.join(output_dir, filename)

#     try:
#         # Generate content using ChatGPT
#         response = client.chat.completions.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant that generates informative content for PDFs."},
#                 {"role": "user", "content": f"Generate content for a PDF on the topic: {prompt}"}
#             ],
#         )
#         content = response.choices[0].message.content

#         # Generate PDF and save it to the specified directory
#         generate_pdf(content, output_filepath, background_image, logo_image)

#         # Return the file path for the generated PDF
#         return output_filepath  # Return the file path as a string
#     except Exception as e:
#         print(f"Error during PDF generation: {str(e)}")  # Log the error
#         return jsonify({'error': f'Failed to generate PDF: {str(e)}'}), 500
           

# @app.route('/upload', methods=['POST'])
# def fileUpload():
#     if request.method == 'POST':
#         # Log the incoming request data
#         print("Request Headers:", request.headers)  # Log the request headers
#         print("Request Form Data:", request.form)    # Log the form data
#         print("Request Files:", request.files)      


#         message = request.form.get('message')
#         # Get the list of uploaded image files
#         files = request.files.getlist('file')
        
#         content_length = request.headers.get('Content-Length')
#         print(f"Content-Length: {content_length} bytes") 
#         # Log the details of the uploaded files
#         if not files:
#             print("No files uploaded.")
#             return jsonify({'message': 'No files uploaded'}), 400
        
#         print("Uploaded files:")
#         filenames = []  # Initialize a list to store filenames
#         for f in files:
#             # print(f"Filename: {f.filename}, Content Type: {f.content_type}, Size: {len(f.read())} bytes")
#             print(f"Media Type: {f.content_type}")  # {{ edit_1 }}
#             f.seek(0)  # Reset file pointer to the beginning after reading
            
#             filename = secure_filename(f.filename)
#             if allowedFile(filename):
#                 print(f"File {filename} is allowed.")  # Log if the file is allowed
#                 f.save(os.path.join(UPLOAD_FOLDER, filename))
#                 filenames.append(filename)  # Add the filename to the list
#             else:
#                 return jsonify({'message': 'File type not allowed'}), 400
        
#         # Get the path of the first uploaded file
#         uploaded_image_path = os.path.join(UPLOAD_FOLDER, filenames[0])  
              
#         # Generate a unique filename using a timestamp
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
#         unique_filename = f'output_{timestamp}.pdf'  # Create a unique filename

#         print("Logging full response data", request.json)
#         # Prepare data for PDF generation
#         pdf_data = {
#             'filename': unique_filename,
#             'background_image': uploaded_image_path,
#             'content': message  # Use the message content for the PDF
#         }
        
        
#         # Call the PDF generation function and get the file path
#         pdf_file_path = generate_pdf_from_data(pdf_data)  # Call the PDF generation function directly
#         print("pdf_file_path:", pdf_file_path)
#         # Check if the PDF file was created successfully
#         if not os.path.exists(pdf_file_path):
#             # Return a JSON error response if the PDF was not created
#             return jsonify({'error': 'PDF file was not created successfully.'}), 500
        
#         print("pdf_file_path after check:", pdf_file_path)
        
#         # Return the PDF file for download
#         try:
#             return send_file(pdf_file_path, as_attachment=True, download_name='output.pdf')  # Specify the download name
#         except Exception as e:
#             # If sending the file fails, return a JSON error response
#             return jsonify({'error': f'Failed to send PDF file: {str(e)}'}), 500


# @app.route('/upload/<filename>')
# def display_image(filename):
#     return send_from_directory('outputImages', filename)  # Updated to pull from outputImages 
# @app.route('/remove_background', methods=['POST'])
# def remove_background():
#     if 'image' not in request.files:
#         return jsonify({"error": "No image file provided"}), 400

#     image_file = request.files['image']
#     if image_file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     processed_image = process_image(image_file, remove_background=True)
#     if processed_image:
#         return send_file(processed_image, mimetype='image/png', as_attachment=True, download_name='background_removed.png')
#     else:
#         return jsonify({"error": "Failed to process image"}), 500

# @app.route('/vectorize', methods=['POST'])
# def vectorize_image_endpoint():
#     if 'image' not in request.files:
#         return jsonify({"error": "No image file provided"}), 400

#     image_file = request.files['image']
#     if image_file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     output_dir = 'temp_vectorized'
#     os.makedirs(output_dir, exist_ok=True)

#     svg_file = jpg_to_svg_and_upscale(image_file, output_dir)
#     if svg_file:
#         with open(svg_file, 'r') as f:
#             svg_content = f.read()
        
#         os.remove(svg_file)
#         os.rmdir(output_dir)
        
#         return jsonify({
#             "response": svg_content,
#             "message": "Image vectorized successfully",
#             "filename": f"vectorized_{image_file.filename.rsplit('.', 1)[0]}.svg"
#         }), 200
#     else:
#         return jsonify({"error": "Failed to vectorize image"}), 500


# if __name__ == '__main__':
#     app.run(debug=True)