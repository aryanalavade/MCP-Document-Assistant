import json

from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

@mcp.tool(
    name = "read_doc_contents",
    description = "Read the contents of a document and return it as a string.",
)
def read_doc_contents(
    doc_id: str = Field(description="Id of the document to read."),
):
    if doc_id not in docs:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    return docs[doc_id]

@mcp.tool( 
          name = "edit_document",
          description = "Edit a document by replacing a string in the documents content with   a new string.",
)
def edit_document(
    doc_id: str = Field(description="Id of the document to edit."),
    old_string: str = Field(description="String to be replaced in the document."),
    new_string: str = Field(description="String to replace the old string with."),
):
    if doc_id not in docs:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    docs[doc_id] = docs[doc_id].replace(old_string, new_string)
    return docs[doc_id]

@mcp.resource(
    "docs://documents", 
    mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())


@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain"
)
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    return docs[doc_id]


@mcp.prompt(
    name="format",
    description="Rewrite the contents of a document in Markdown format.",
)
def format_document(
    doc_id: str:Field(description="Id of the document to format")
    ) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document to be written with markdown syntax. 
    The id of the document you need to reformt is:
    <doc_id>
    {doc_id}
    </doc_id>
    
    Add in headers, bullet points, tables, etc as necessary. Feel free to add in examples, code snippets, and other formatting to make the document more readable.
    Use the 'edit_document' tool to make changes to the document. You can call the tool multiple times if necessary. After the document has been reformatted, use the 'read_doc_contents' tool to read the contents of the document and return it as a string.

"""
return [
base.UserMessage(prompt)]

    if doc_id not in docs:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    return (
        "Rewrite the following document in clear, well-structured Markdown. "
        "Preserve all factual details, do not add information, and return only "
        "the rewritten document.\n\n"
        f"Document ({doc_id}):\n{docs[doc_id]}"
    )


@mcp.prompt(
    name="summarize",
    description="Summarize a document.",
)
def summarize_document(doc_id: str) -> str:
    """Summarize the specified document.

    Args:
        doc_id: Id of the document to summarize.
    """
    if doc_id not in docs:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    return (
        "Summarize the following document concisely. Include its key points "
        "and do not add information not supported by the text.\n\n"
        f"Document ({doc_id}):\n{docs[doc_id]}"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
