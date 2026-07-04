import re
import xml.etree.ElementTree as ET
from typing import List, Optional, Tuple

from app.ingestion.schemas import PageText, SectionBlock


TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}


def clean_xml_text(text: Optional[str]) -> str:
    if not text:
        return ""

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def slugify_heading(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9α-ωΑ-Ω]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def extract_text_from_element(element: ET.Element) -> str:
    parts = []

    for text in element.itertext():
        cleaned = clean_xml_text(text)
        if cleaned:
            parts.append(cleaned)

    return clean_xml_text(" ".join(parts))


def estimate_page_range(section_text: str, pages: List[PageText]) -> Tuple[int, int]:
    if not pages:
        return 1, 1

    sample = clean_xml_text(section_text[:300]).lower()

    if not sample:
        return pages[0].page_number, pages[-1].page_number

    matching_pages = []

    for page in pages:
        page_text = clean_xml_text(page.text).lower()

        if sample[:120] in page_text or any(
            phrase in page_text for phrase in sample.split(". ")[:2] if len(phrase) > 40
        ):
            matching_pages.append(page.page_number)

    if matching_pages:
        return min(matching_pages), max(matching_pages)

    return pages[0].page_number, pages[-1].page_number


def extract_title(root: ET.Element) -> Optional[str]:
    title_el = root.find(".//tei:titleStmt/tei:title", TEI_NS)

    if title_el is None:
        return None

    title = extract_text_from_element(title_el)
    return title or None


def extract_author(root: ET.Element) -> Optional[str]:
    author_el = root.find(".//tei:sourceDesc//tei:author", TEI_NS)

    if author_el is None:
        return None

    author = extract_text_from_element(author_el)
    return author or None


def extract_abstract(root: ET.Element, pages: List[PageText]) -> Optional[SectionBlock]:
    abstract_el = root.find(".//tei:profileDesc/tei:abstract", TEI_NS)

    if abstract_el is None:
        return None

    text = extract_text_from_element(abstract_el)

    if not text:
        return None

    start_page, end_page = estimate_page_range(text, pages)

    return SectionBlock(
        section="abstract",
        text=f"ABSTRACT\n{text}",
        start_page=start_page,
        end_page=end_page,
        char_count=len(text),
    )


def extract_body_sections(root: ET.Element, pages: List[PageText]) -> List[SectionBlock]:
    blocks: List[SectionBlock] = []

    body = root.find(".//tei:text/tei:body", TEI_NS)

    if body is None:
        return blocks

    divs = body.findall(".//tei:div", TEI_NS)

    for div in divs:
        head_el = div.find("tei:head", TEI_NS)

        if head_el is None:
            continue

        heading = extract_text_from_element(head_el)

        if not heading:
            continue

        section_name = slugify_heading(heading)
        body_text = extract_text_from_element(div)

        if not body_text:
            continue

        text = f"{heading}\n{body_text}"
        start_page, end_page = estimate_page_range(text, pages)

        blocks.append(
            SectionBlock(
                section=section_name,
                text=text,
                start_page=start_page,
                end_page=end_page,
                char_count=len(text),
            )
        )

    return blocks


def parse_grobid_tei(tei_xml: str, pages: List[PageText]) -> Tuple[Optional[str], Optional[str], List[SectionBlock]]:
    root = ET.fromstring(tei_xml)

    title = extract_title(root)
    author = extract_author(root)

    section_blocks: List[SectionBlock] = []

    abstract_block = extract_abstract(root, pages)

    if abstract_block:
        section_blocks.append(abstract_block)

    section_blocks.extend(extract_body_sections(root, pages))

    return title, author, section_blocks
