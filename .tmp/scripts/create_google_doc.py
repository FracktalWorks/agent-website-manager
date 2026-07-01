#!/usr/bin/env python3
"""
Create a new Google Doc with specified title and optional content.
Part of the Business Planning Agent toolkit.
"""

import os
import sys
import json
import argparse
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]


def get_credentials():
    """
    Get OAuth2 credentials for Google Docs API.
    Uses token.json if available, otherwise prompts for authorization.
    """
    creds = None

    if os.path.exists('token.json'):
        try:
            with open('token.json', 'r') as token:
                token_data = json.load(token)
                creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        except Exception as e:
            print(f"Error loading token: {e}")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def create_google_doc(title, initial_content=None, folder_id=None):
    """
    Create a new Google Doc.

    Args:
        title: Title of the document
        initial_content: Optional initial text content
        folder_id: Optional Google Drive folder ID to place the document

    Returns:
        Dictionary with document ID and URL
    """
    creds = get_credentials()
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    # Create the document
    doc_body = {'title': title}
    doc = docs_service.documents().create(body=doc_body).execute()
    doc_id = doc.get('documentId')

    print(f"Created document: {title}")
    print(f"Document ID: {doc_id}")

    # Add initial content if provided
    if initial_content:
        requests = [
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': initial_content
                }
            }
        ]
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        print("Added initial content")

    # Move to folder if specified
    if folder_id:
        file = drive_service.files().get(fileId=doc_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents', []))
        drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()
        print(f"Moved to folder: {folder_id}")

    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    return {
        'document_id': doc_id,
        'title': title,
        'url': doc_url
    }


def main():
    parser = argparse.ArgumentParser(description='Create a new Google Doc')
    parser.add_argument('--title', required=True, help='Title of the document')
    parser.add_argument('--content', help='Initial content (text or file path)')
    parser.add_argument('--content-file', help='Path to file with initial content')
    parser.add_argument('--folder-id', help='Google Drive folder ID')
    parser.add_argument('--output', help='Output JSON file path')

    args = parser.parse_args()

    # Get content from file if specified
    initial_content = args.content
    if args.content_file and os.path.exists(args.content_file):
        with open(args.content_file, 'r', encoding='utf-8') as f:
            initial_content = f.read()

    try:
        result = create_google_doc(
            title=args.title,
            initial_content=initial_content,
            folder_id=args.folder_id
        )

        print(f"\nDocument URL: {result['url']}")

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Result saved to: {args.output}")

        return result

    except Exception as e:
        print(f"Error creating document: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
