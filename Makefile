# Friet van Desire — build SID remixes from MIDI research material
#
# Pipeline: extract -> compose -> synth.
#   make friet           the release SID (175 BPM, hoover lead)
#   make preview-friet   .mp3 preview of the release
#   make player          standalone C64 .prg (embeds friet.sid + lyric ticker)
#   make preview-clean   song-faithful workstage render (130 BPM)
#   make preview-melody  vocal-only workstage (verification)
.PHONY: all clean analyze extract compose synth \
        clean-pipeline melody-only friet lab \
        preview preview-clean preview-melody preview-friet preview-lab player

SHELL      := /bin/bash
.ONESHELL:

PYTHON     := .venv/bin/python
SRC_DIR    := src
OUT_DIR    := out
MIDI_DIR   := midi
TOOLS_DIR  := tools

SPEC       := docs/song_spec.yaml
LAYERS     := docs/song_layers.yaml
COMP       := docs/composition.yaml

CLEAN_SID  := $(OUT_DIR)/friet_clean.sid
CLEAN_MP3  := $(OUT_DIR)/friet_clean.mp3
MELODY_SID := $(OUT_DIR)/friet_melody_only.sid
MELODY_MP3 := $(OUT_DIR)/friet_melody_only.mp3
FRIET_SID  := $(OUT_DIR)/friet.sid
FRIET_MP3  := $(OUT_DIR)/friet.mp3
FRIET_PRG  := $(OUT_DIR)/friet.prg
LAB_SID    := $(OUT_DIR)/lab.sid
LAB_MP3    := $(OUT_DIR)/lab.mp3

PREVIEW_SECONDS ?= 90
LAB_SECONDS     ?= 15

all: clean-pipeline melody-only friet preview-clean preview-melody preview-friet

# --- research ----
analyze:
	$(PYTHON) $(SRC_DIR)/analyze_midi.py

# --- pipeline (extract -> compose -> synth) ----
# Phase 1: MIDI -> docs/song_spec.yaml (patterns) + docs/song_layers.yaml
#          (verbatim T5/T7/T11/T12/T13 note lists). The MIDI isn't read again.
extract: $(SPEC) $(LAYERS)
$(SPEC) $(LAYERS): $(SRC_DIR)/extract_patterns.py $(MIDI_DIR)/Gala_Freed_From_Desire.mid
	$(PYTHON) $<

# Phase 2: spec + layers -> docs/composition.yaml. No MIDI access.
compose: $(COMP)
$(COMP): $(SRC_DIR)/compose.py $(SPEC) $(LAYERS)
	$(PYTHON) $<

# Phase 3: composition -> PSID. Reads only composition.yaml.
synth: $(CLEAN_SID)
$(CLEAN_SID): $(SRC_DIR)/synth.py $(COMP)
	$(PYTHON) $<

clean-pipeline: $(CLEAN_SID)

preview-clean: $(CLEAN_MP3)
$(CLEAN_MP3): $(CLEAN_SID)
	$(TOOLS_DIR)/render-preview.sh $< $@ $(PREVIEW_SECONDS)

# Vocal-only verification build — useful when the surrounding mix obscures
# the melody and you need to confirm the notes themselves.
melody-only: $(MELODY_SID)
$(MELODY_SID): $(SRC_DIR)/compose.py $(SRC_DIR)/synth.py $(SPEC) $(LAYERS)
	MELODY_ONLY=1 $(PYTHON) $(SRC_DIR)/compose.py
	$(PYTHON) $(SRC_DIR)/synth.py
	cp $(CLEAN_SID) $@
	$(PYTHON) $(SRC_DIR)/compose.py
	$(PYTHON) $(SRC_DIR)/synth.py

preview-melody: $(MELODY_MP3)
$(MELODY_MP3): $(MELODY_SID)
	$(TOOLS_DIR)/render-preview.sh $< $@ $(PREVIEW_SECONDS)

# Release build — 175 BPM with hoover lead. This is the final SID.
friet: $(FRIET_SID)
$(FRIET_SID): $(SRC_DIR)/compose.py $(SRC_DIR)/synth.py $(SPEC) $(LAYERS)
	FAST=1 $(PYTHON) $(SRC_DIR)/compose.py
	$(PYTHON) $(SRC_DIR)/synth.py
	cp $(CLEAN_SID) $@
	$(PYTHON) $(SRC_DIR)/compose.py
	$(PYTHON) $(SRC_DIR)/synth.py

preview-friet: $(FRIET_MP3)
$(FRIET_MP3): $(FRIET_SID)
	$(TOOLS_DIR)/render-preview.sh $< $@ $(PREVIEW_SECONDS)

# Experimental sandbox — short loop of a fragment + hand-written
# beat/bass pattern. Tweak src/lab.py SETTINGS and re-run `make lab`.
lab: $(LAB_MP3)
$(LAB_SID): $(SRC_DIR)/lab.py $(SRC_DIR)/synth.py $(LAYERS)
	$(PYTHON) $(SRC_DIR)/lab.py
$(LAB_MP3): $(LAB_SID)
	$(TOOLS_DIR)/render-preview.sh $< $@ $(LAB_SECONDS)
preview-lab: $(LAB_MP3)

# Stand-alone C64 .prg that plays the release SID with a lyric ticker.
# Build with KickAssembler (kickass/KickAss.jar). Run with `x64sc out/friet.prg`.
player: $(FRIET_PRG)
$(FRIET_PRG): $(SRC_DIR)/build_player.py $(SRC_DIR)/player/friet.asm \
              $(FRIET_SID) docs/melody_lyrics.yaml
	$(PYTHON) $(SRC_DIR)/build_player.py

# --- previews ----
preview: preview-clean preview-melody preview-friet

clean:
	rm -f $(OUT_DIR)/*.sid $(OUT_DIR)/*.wav $(OUT_DIR)/*.mp3 $(OUT_DIR)/*.prg
	rm -f docs/lab_composition.yaml
	rm -f /tmp/freed*.s /tmp/freed*.prg
