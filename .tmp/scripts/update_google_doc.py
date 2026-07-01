#!/usr/bin/env python3
"""
Update an existing Google Doc - append, replace, or insert content.
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

load_dotenv()

SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]


def get_credentials():
    """Get OAuth2 credentials for Google Docs API."""
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


def extract_doc_id(url_or_id):
    """Extract document ID from URL or return as-is if already an ID."""
    if '/d/' in url_or_id:
        return url_or_id.split('/d/')[1].split('/')[0]
    return url_or_id


def get_document_end_index(docs_service, doc_id):
    """Get the end index of the document content."""
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = doc.get('body', {}).get('content', [])
    if content:
        last_element = content[-1]
        return last_element.get('endIndex', 1) - 1
    return 1


def update_google_doc(doc_id, content, mode='append', find_text=None, heading_level=None):
    """
    Update a Google Doc.

    Args:
        doc_id: Document ID or URL
        content: Text content to add
        mode: 'append', 'prepend', 'replace', or 'insert_after'
        find_text: Text to find (for replace or insert_after mode)
        heading_level: Optional heading level (1-6) for the content

    Returns:
        Dictionary with update status
    """
    creds = get_credentials()
    docs_service = build('docs', 'v1', credentials=creds)
    
    doc_id = extract_doc_id(doc_id)
    
    # Get current document
    doc = docs_service.documents().get(documentId=doc_id).execute()
    doc_title = doc.get('title', 'Untitled')
    
    requests = []
    
    if mode == 'append':
        # Append at the end
        end_index = get_document_end_index(docs_service, doc_id)
        requests.append({
            'insertText': {
                'location': {'index': end_index},
                'text': '\n' + content
            }
        })
        
    elif mode == 'prepend':
        # Insert at the beginning
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': content + '\n'
            }
        })
        
    elif mode == 'replace' and find_text:
        # Replace all occurrences
        requests.append({
            'replaceAllText': {
                'containsText': {
                    'text': find_text,
                    'matchCase': True
                },
                'replaceText': content
            }
        })
        
    elif mode == 'insert_after' and find_text:
        # Find text and insert after it
        body_content = doc.get('body', {}).get('content', [])
        for element in body_content:
            if 'paragraph' in element:
                for text_run in element['paragraph'].get('elements', []):
                    if 'textRun' in text_run:
                        text = text_run['textRun'].get('content', '')
                        if find_text in text:
                            insert_index = text_run.get('endIndex', 1)
                            requests.append({
                                'insertText': {
                                    'location': {'index': insert_index - 1},
                                    'text': '\n' + content
                                }
                            })
                            break
    
    # Apply heading formatting if specified
    if heading_level and requests and 'insertText' in requests[0]:
        insert_location = requests[0]['insertText']['location']['index']
        content_length = len(content)
        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': insert_location,
                    'endIndex': insert_location + content_length
                },
                'paragraphStyle': {
                    'namedStyleType': f'HEADING_{heading_level}'
                },
                'fields': 'namedStyleType'
            }
        })
    
    if requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        print(f"Updated document: {doc_title}")
        print(f"Mode: {mode}")
    else:
        print("No updates to apply")
    
    return {
        'document_id': doc_id,
        'title': doc_title,
        'mode': mode,
        'url': f"https://docs.google.com/document/d/{doc_id}/edit"
    }


def main():
    parser = argparse.ArgumentParser(description='Update a Google Doc')
    parser.add_argument('--doc-id', required=True, help='Document ID or URL')
    parser.add_argument('--content', help='Content to add')
    parser.add_argument('--content-file', help='Path to file with content')
    parser.add_argument('--mode', choices=['append', 'prepend', 'replace', 'insert_after'],
                        default='append', help='Update mode')
    parser.add_argument('--find-text', help='Text to find (for replace/insert_after)')
    parser.add_argument('--heading', type=int, choices=[1, 2, 3, 4, 5, 6],
                        help='Apply heading style (1-6)')
    parser.add_argument('--output', help='Output JSON file path')

    args = parser.parse_args()

    content = args.content
    if args.content_file and os.path.exists(args.content_file):
        with open(args.content_file, 'r', encoding='utf-8') as f:
            content = f.read()

    if not content:
        print("Error: No content provided")
        sys.exit(1)

    try:
        result = update_google_doc(
            doc_id=args.doc_id,
            content=content,
            mode=args.mode,
            find_text=args.find_text,
            heading_level=args.heading
        )

        print(f"\nDocument URL: {result['url']}")

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Result saved to: {args.output}")

        return result

    except Exception as e:
        print(f"Error updating document: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
