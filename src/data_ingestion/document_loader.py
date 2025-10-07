"""Document loading utilities for various file formats."""

import os
from typing import List, Dict, Any
from pathlib import Path
from langchain.docstore.document import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
)


class DocumentLoader:
    """Load documents from various file formats."""

    SUPPORTED_EXTENSIONS = {
        '.pdf': PyPDFLoader,
        '.txt': TextLoader,
        '.html': UnstructuredHTMLLoader,
        '.md': UnstructuredMarkdownLoader,
    }

    @classmethod
    def load_document(cls, file_path: str) -> List[Document]:
        """
        Load a single document from file path.

        Args:
            file_path: Path to the document file

        Returns:
            List of Document objects
        """
        file_extension = Path(file_path).suffix.lower()

        if file_extension not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {file_extension}. "
                f"Supported types: {list(cls.SUPPORTED_EXTENSIONS.keys())}"
            )

        loader_class = cls.SUPPORTED_EXTENSIONS[file_extension]
        loader = loader_class(file_path)

        documents = loader.load()

        # Add source metadata
        for doc in documents:
            doc.metadata['source'] = file_path
            doc.metadata['filename'] = Path(file_path).name

        return documents

    @classmethod
    def load_directory(cls, directory_path: str, recursive: bool = True) -> List[Document]:
        """
        Load all supported documents from a directory.

        Args:
            directory_path: Path to directory containing documents
            recursive: Whether to search subdirectories

        Returns:
            List of all loaded Document objects
        """
        all_documents = []
        directory = Path(directory_path)

        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        # Get file pattern
        pattern = "**/*" if recursive else "*"

        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in cls.SUPPORTED_EXTENSIONS:
                try:
                    documents = cls.load_document(str(file_path))
                    all_documents.extend(documents)
                    print(f"✓ Loaded: {file_path.name} ({len(documents)} chunks)")
                except Exception as e:
                    print(f"✗ Error loading {file_path.name}: {str(e)}")

        return all_documents

    @classmethod
    def load_from_string(cls, content: str, metadata: Dict[str, Any] = None) -> Document:
        """
        Create a Document from a string.

        Args:
            content: Text content
            metadata: Optional metadata dictionary

        Returns:
            Document object
        """
        return Document(
            page_content=content,
            metadata=metadata or {}
        )


# Example FAQ data structure
EXAMPLE_FAQ_DATA = [
    {
        "question": "How do I track my order?",
        "answer": "You can track your order by logging into your account and visiting the 'Orders' section. "
                 "Click on the order number to see detailed tracking information. You'll also receive "
                 "tracking updates via email and SMS if you've opted in for notifications.",
        "category": "Orders"
    },
    {
        "question": "What is your return policy?",
        "answer": "We offer a 30-day return policy for most items. Products must be unused and in original "
                 "packaging. To initiate a return, go to your order history, select the item, and click "
                 "'Return Item'. You'll receive a prepaid shipping label via email within 24 hours.",
        "category": "Returns"
    },
    {
        "question": "How long does shipping take?",
        "answer": "Standard shipping takes 5-7 business days. Express shipping (2-3 business days) and "
                 "overnight shipping are also available at checkout. Free standard shipping is included "
                 "on orders over $50.",
        "category": "Shipping"
    },
    {
        "question": "Do you ship internationally?",
        "answer": "Yes, we ship to over 100 countries worldwide. International shipping times vary by "
                 "destination (typically 7-21 business days). Customs fees and import duties may apply "
                 "and are the responsibility of the customer.",
        "category": "Shipping"
    },
    {
        "question": "How do I reset my password?",
        "answer": "Click 'Forgot Password' on the login page. Enter your email address and we'll send you "
                 "a password reset link. The link expires after 24 hours for security. If you don't receive "
                 "the email, check your spam folder or contact support.",
        "category": "Account"
    },
    {
        "question": "What payment methods do you accept?",
        "answer": "We accept Visa, MasterCard, American Express, Discover, PayPal, Apple Pay, and Google Pay. "
                 "All transactions are encrypted and secure. We do not store your full credit card information.",
        "category": "Payment"
    },
]


def load_faq_data() -> List[Document]:
    """
    Convert FAQ data into Document objects.

    Returns:
        List of Document objects from FAQ data
    """
    documents = []

    for faq in EXAMPLE_FAQ_DATA:
        content = f"Question: {faq['question']}\n\nAnswer: {faq['answer']}"
        metadata = {
            "source": "faq",
            "category": faq['category'],
            "question": faq['question']
        }
        documents.append(Document(page_content=content, metadata=metadata))

    return documents
