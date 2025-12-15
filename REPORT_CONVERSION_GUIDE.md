# How to Convert the Recommendation Engine Report to Word/PDF

This guide explains how to convert the visual markdown report into a professional Word document or PDF for your project documentation.

## Method 1: Using Pandoc (Recommended)

### Install Pandoc
```bash
# Windows (using Chocolatey)
choco install pandoc

# Mac
brew install pandoc

# Or download from: https://pandoc.org/installing.html
```

### Convert to Word (DOCX)
```bash
cd "c:\Users\talgo\Documents\smarTrip project\trip-recommendations"

pandoc RECOMMENDATION_ENGINE_REPORT_VISUAL.md -o RecommendationEngine.docx --toc --toc-depth=3 -s
```

### Convert to PDF (requires LaTeX)
```bash
# Install LaTeX first
# Windows: https://miktex.org/download
# Mac: brew install mactex

pandoc RECOMMENDATION_ENGINE_REPORT_VISUAL.md -o RecommendationEngine.pdf --toc --toc-depth=3 -s -V geometry:margin=1in
```

### Advanced Options
```bash
# With custom styling
pandoc RECOMMENDATION_ENGINE_REPORT_VISUAL.md \
  -o RecommendationEngine.docx \
  --toc \
  --toc-depth=3 \
  --reference-doc=custom-template.docx \
  -s

# With metadata
pandoc RECOMMENDATION_ENGINE_REPORT_VISUAL.md \
  -o RecommendationEngine.pdf \
  --toc \
  --metadata title="SmartTrip Recommendation Engine" \
  --metadata author="SmartTrip Team" \
  --metadata date="December 2025" \
  -V geometry:margin=1in \
  -V fontsize=11pt \
  -s
```

---

## Method 2: Using VS Code Extensions

### Install Extensions
1. Open VS Code
2. Install "Markdown PDF" extension
3. Install "Markdown Preview Mermaid Support" for diagrams

### Convert
1. Open `RECOMMENDATION_ENGINE_REPORT_VISUAL.md`
2. Right-click in the editor
3. Select "Markdown PDF: Export (pdf)" or "Markdown PDF: Export (docx)"

---

## Method 3: Using Online Tools

### Markdown to Word
1. Go to https://www.markdowntoword.com/
2. Upload `RECOMMENDATION_ENGINE_REPORT_VISUAL.md`
3. Download the generated .docx file

### Markdown to PDF
1. Go to https://md2pdf.netlify.app/
2. Paste the markdown content
3. Download PDF

**Note:** Online tools may not render Mermaid diagrams. For best results with diagrams, use Method 1 (Pandoc) or Method 2 (VS Code).

---

## Method 4: Using Microsoft Word Directly

### Steps
1. Copy the entire content of `RECOMMENDATION_ENGINE_REPORT_VISUAL.md`
2. Open Microsoft Word
3. Paste the content
4. Word will auto-format most markdown
5. Manually format:
   - Apply heading styles (Heading 1, 2, 3)
   - Format code blocks with monospace font
   - Add page breaks where indicated
   - Format tables properly

### For Mermaid Diagrams
1. Go to https://mermaid.live/
2. Copy each Mermaid diagram from the markdown
3. Paste into Mermaid Live Editor
4. Export as PNG or SVG
5. Insert images into Word document

---

## Method 5: Using Google Docs

### Steps
1. Open Google Docs
2. Install "Docs to Markdown" extension (for reverse compatibility)
3. Paste markdown content
4. Use built-in formatting tools
5. Export as:
   - File → Download → Microsoft Word (.docx)
   - File → Download → PDF Document (.pdf)

---

## Rendering Mermaid Diagrams

The report includes Mermaid diagrams (flowcharts, sequence diagrams, etc.) that need special handling:

### Option A: Use Mermaid CLI
```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Extract diagrams to separate files
# Then convert each diagram:
mmdc -i diagram.mmd -o diagram.png
```

### Option B: Use Online Mermaid Editor
1. Go to https://mermaid.live/
2. Copy each Mermaid code block from the markdown
3. Editor will render it visually
4. Click "Actions" → "PNG" or "SVG"
5. Download and insert into Word/PDF

### Option C: Use VS Code Mermaid Extension
1. Install "Markdown Preview Mermaid Support" extension
2. Open markdown file
3. Right-click on preview → "Save as HTML"
4. Print HTML to PDF from browser

---

## Recommended Workflow for Professional Output

### Step 1: Convert with Pandoc
```bash
pandoc RECOMMENDATION_ENGINE_REPORT_VISUAL.md -o RecommendationEngine.docx --toc --toc-depth=3 -s
```

### Step 2: Render Mermaid Diagrams
1. Go to https://mermaid.live/
2. Export each diagram as PNG (high resolution)
3. Name them: `diagram-1-system-components.png`, `diagram-2-sequence.png`, etc.

### Step 3: Open in Word and Enhance
1. Open `RecommendationEngine.docx` in Microsoft Word
2. Insert rendered Mermaid diagrams in their appropriate sections
3. Apply professional formatting:
   - Use built-in styles for headings
   - Apply "Intense Reference" style for code blocks
   - Apply table styles
   - Add header/footer with document title and page numbers
   - Add cover page

### Step 4: Final Touches
- Add company logo to header
- Adjust margins: 1 inch all sides
- Set font: Calibri or Arial 11pt
- Ensure page breaks are correct
- Add table of contents (References → Table of Contents)
- Number sections automatically

### Step 5: Export to PDF
- File → Save As → PDF
- Or File → Export → Create PDF/XPS

---

## Styling Tips for Word/PDF

### Recommended Fonts
- **Headings:** Calibri Light or Arial, 14-18pt, Bold
- **Body:** Calibri or Arial, 11pt
- **Code:** Consolas or Courier New, 10pt
- **Tables:** Calibri, 10pt

### Color Scheme
- **Primary Heading:** RGB(0, 102, 204) - Blue
- **Secondary Heading:** RGB(68, 68, 68) - Dark Gray
- **Code Blocks:** Light gray background RGB(245, 245, 245)
- **Tables:** Alternating row colors (white/light blue)

### Page Layout
- **Margins:** 1 inch all sides
- **Line Spacing:** 1.15 or 1.5 for body text
- **Section Spacing:** 12pt before, 6pt after headings
- **Page Breaks:** Before major sections (Part I, Part II, etc.)

### Table of Contents
```
Add automatic TOC in Word:
1. References tab → Table of Contents
2. Choose "Automatic Table 1"
3. Update when sections change
```

---

## Sample Pandoc Command for Best Results

```bash
pandoc RECOMMENDATION_ENGINE_REPORT_VISUAL.md \
  -o RecommendationEngine.pdf \
  --toc \
  --toc-depth=3 \
  --number-sections \
  --highlight-style=tango \
  --pdf-engine=xelatex \
  -V geometry:margin=1in \
  -V fontsize=11pt \
  -V documentclass=report \
  -V papersize=letter \
  -V colorlinks=true \
  -V linkcolor=blue \
  -V urlcolor=blue \
  --metadata title="SmartTrip Recommendation Engine - Technical Documentation" \
  --metadata subtitle="Algorithm Specification & Implementation Guide" \
  --metadata author="SmartTrip Development Team" \
  --metadata date="December 14, 2025" \
  -s
```

---

## Troubleshooting

### Issue: Mermaid diagrams don't render
**Solution:** Use Mermaid Live Editor to export as images, then insert manually.

### Issue: Tables are not formatted properly
**Solution:** In Word, select table → Table Design → Apply table style.

### Issue: Code blocks lose formatting
**Solution:** Apply "Code" or "Intense Reference" style in Word.

### Issue: Page breaks in wrong places
**Solution:** 
- In markdown, use: `<div style="page-break-after: always;"></div>`
- In Word, manually insert page breaks where needed

### Issue: PDF fonts look wrong
**Solution:** Use `--pdf-engine=xelatex` instead of default pdflatex.

---

## Final Checklist

Before submitting the document:

- [ ] All Mermaid diagrams rendered and inserted
- [ ] Table of contents generated and up-to-date
- [ ] Page numbers added to footer
- [ ] Cover page includes: Title, Subtitle, Authors, Date, Logo
- [ ] All headings use consistent styles
- [ ] Code blocks are properly formatted with monospace font
- [ ] Tables have proper borders and styles
- [ ] Page breaks are in correct locations
- [ ] No orphan headings (heading at bottom of page)
- [ ] Hyperlinks work correctly
- [ ] Document saved as both .docx and .pdf
- [ ] File names: `SmartTrip_Recommendation_Engine_v1.0.docx/pdf`

---

## Recommended Tools Summary

| Task | Tool | Platform | Notes |
|------|------|----------|-------|
| **Primary Conversion** | Pandoc | All | Best quality, handles most markdown |
| **Diagram Rendering** | Mermaid Live | Web | Export diagrams as PNG/SVG |
| **Quick Preview** | VS Code Extensions | All | Fast iteration during writing |
| **Final Formatting** | Microsoft Word | Windows/Mac | Professional polish |
| **PDF Export** | Word or Pandoc | All | High quality output |

---

## Need Help?

- Pandoc Manual: https://pandoc.org/MANUAL.html
- Mermaid Documentation: https://mermaid.js.org/
- Markdown Guide: https://www.markdownguide.org/

---

**Good luck with your project documentation!**
