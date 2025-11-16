"""
Vision-based syllabus extraction service
Supports: PDFs, images (JPG, PNG), plain text
"""
import base64
from typing import List, Dict, Any, Tuple
from PyPDF2 import PdfReader
from PIL import Image
from io import BytesIO

from app.clients.ai_client import get_ai_client
from app.models import Task


def pdf_to_images(pdf_bytes: bytes) -> List[str]:
    """
    Convert PDF pages to base64-encoded images for vision API

    Args:
        pdf_bytes: PDF file content

    Returns:
        List of base64-encoded PNG images (one per page)
    """
    try:
        from pdf2image import convert_from_bytes

        # Convert PDF to images
        images = convert_from_bytes(pdf_bytes, dpi=150)

        encoded_images = []
        for img in images:
            # Convert to PNG bytes
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            # Encode to base64
            img_b64 = base64.b64encode(buffer.read()).decode('utf-8')
            encoded_images.append(img_b64)

        return encoded_images

    except ImportError:
        # Fallback: Try text extraction if pdf2image not available
        raise ImportError("pdf2image not installed. Install with: pip install pdf2image")


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF (fallback if vision not needed)"""
    try:
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")


def process_syllabus_file(file_content: str, filename: str = "") -> Tuple[str, List[str], str]:
    """
    Process uploaded file and determine format

    Args:
        file_content: Base64 encoded file
        filename: Original filename (helps determine type)

    Returns:
        Tuple of (text_content, image_list, file_type)
    """
    try:
        decoded = base64.b64decode(file_content)
    except Exception as e:
        raise ValueError(f"Invalid base64 content: {str(e)}")

    filename_lower = filename.lower()

    # Check if PDF
    if filename_lower.endswith('.pdf') or decoded[:4] == b'%PDF':
        try:
            # Try vision-based extraction first
            images = pdf_to_images(decoded)
            return None, images, "pdf_vision"
        except:
            # Fallback to text extraction
            text = extract_text_from_pdf(decoded)
            return text, None, "pdf_text"

    # Check if image
    elif any(filename_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
        # It's already an image, just pass the base64
        return None, [file_content], "image"

    # Assume plain text
    else:
        try:
            text = decoded.decode('utf-8')
            return text, None, "text"
        except:
            raise ValueError("Unsupported file format. Use PDF, image, or text file.")


def extract_tasks_from_syllabus(
    syllabus_text: str = None,
    file_content: str = None,
    filename: str = "",
    user_id: str = None
) -> Tuple[List[Task], List[str]]:
    """
    Extract tasks from syllabus using AI vision/text analysis

    Args:
        syllabus_text: Raw text of syllabus (if provided directly)
        file_content: Base64 encoded file content
        filename: Original filename
        user_id: User ID to associate with tasks

    Returns:
        Tuple of (list of Task objects, list of warnings)
    """
    warnings = []

    # Process input
    if file_content:
        text, images, file_type = process_syllabus_file(file_content, filename)
    elif syllabus_text:
        text = syllabus_text
        images = None
        file_type = "text"
    else:
        raise ValueError("Either syllabus_text or file_content must be provided")

    # Call AI to extract tasks
    ai_client = get_ai_client()

    try:
        result = ai_client.extract_syllabus_tasks(
            syllabus_text=text,
            image_base64=images[0] if images and len(images) == 1 else None,
            pdf_images=images if images and len(images) > 1 else None
        )
    except Exception as e:
        raise Exception(f"AI extraction failed: {str(e)}")

    # Parse result into Task objects
    tasks_data = result.get("tasks", [])

    if not tasks_data:
        warnings.append("No tasks found in syllabus")

    tasks = []
    for task_dict in tasks_data:
        # Check for missing dates
        if task_dict.get("due") is None:
            if task_dict.get("notes"):
                task_dict["notes"] = (task_dict.get("notes", "") + " [Due date unclear]").strip()
            else:
                task_dict["notes"] = "[Due date unclear]"

        # Create Task object
        task = Task(
            user_id=user_id,
            title=task_dict.get("title", "Untitled Task"),
            due_date=task_dict.get("due"),
            task_type=task_dict.get("type", "other"),
            weight=task_dict.get("weight"),
            notes=task_dict.get("notes"),
            completed=False
        )
        tasks.append(task)

    # Add warnings for tasks with missing dates
    missing_dates = [t.title for t in tasks if t.due_date is None]
    if missing_dates:
        warnings.append(f"{len(missing_dates)} tasks with unclear due dates")

    return tasks, warnings
