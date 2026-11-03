# Presentation & Technical Report Materials

This folder contains the slide decks, technical report PDF generator, and diagram generation scripts for **MelodyLoop**.

## Slide Decks
- `MelodyLoop_Presentation_Professional.pptx`: 17-slide academic widescreen (16:9) presentation with embedded speaker notes.
- `MelodyLoop_Presentation.pptx`: Alternative academic slide deck.

## Generation Scripts
To regenerate presentations or figures from anywhere in the repository:
```bash
# Generate the 17-slide academic PowerPoint deck
python presentation/generate_presentation_professional.py

# Generate the alternative slide deck
python presentation/generate_presentation.py

# Generate presentation diagram figures
python presentation/build_presentation_figures.py

# Generate technical report diagram figures
python presentation/generate_doc_figures.py

# Compile the complete 20-chapter PDF Technical Report & Viva Guide
python presentation/generate_full_workflow_pdf.py
```
