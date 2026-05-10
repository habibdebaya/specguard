"""
Encode an aerospace safety standard's PSSA and SPEC requirements from a PDF
into a Z3-ready Python file.

The user supplies the PDF and a free-text section description. Claude Opus 4.7
reads the PDF, identifies the requirements within the section, and emits a
file that exposes PSSA_REQUIREMENTS and SPEC_REQUIREMENTS lists in the same
shape as examples/arp4754b_appendix_e.py.

Set ANTHROPIC_API_KEY before running. Use --dry-run to assemble and print the
prompt without making the API call.
"""

import argparse
import base64
from pathlib import Path


PROMPT_TEMPLATE = Path(__file__).parent / "prompts" / "encode.md"


def build_prompt(section):
    template = PROMPT_TEMPLATE.read_text()
    return template.replace("{SECTION}", section)


def strip_markdown_fences(text):
    text = text.strip()
    if text.startswith("```"):
        first_newline = text.find("\n")
        text = text[first_newline + 1:] if first_newline != -1 else text
    if text.endswith("```"):
        text = text[: text.rfind("```")]
    return text.strip() + "\n"


def call_claude(pdf_bytes, prompt, model):
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=16000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": base64.standard_b64encode(pdf_bytes).decode(),
                    },
                },
                {"type": "text", "text": prompt},
            ],
        }],
    )
    return response.content[0].text


def main():
    parser = argparse.ArgumentParser(
        description="Encode a PDF section into a Z3-ready requirements file."
    )
    parser.add_argument("pdf", help="Path to the PDF.")
    parser.add_argument(
        "--section",
        required=True,
        help="Free-text description of the section to encode "
             "(e.g. 'Appendix E').",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Where to write the generated requirements file.",
    )
    parser.add_argument(
        "--model",
        default="claude-opus-4-7",
        help="Claude model to use.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the assembled prompt and exit without calling the API.",
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    pdf_bytes = pdf_path.read_bytes()

    prompt = build_prompt(args.section)

    if args.dry_run:
        print(prompt)
        print(f"\n[would send PDF: {pdf_path} ({len(pdf_bytes)} bytes), model: {args.model}]")
        return

    out_text = call_claude(pdf_bytes, prompt, args.model)
    out_text = strip_markdown_fences(out_text)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out_text)
    print(f"Wrote {out_path} ({len(out_text)} chars)")


if __name__ == "__main__":
    main()
