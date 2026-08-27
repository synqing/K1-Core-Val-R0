# Evidence

Naming convention:

    evidence/VAL-Gn-<YYYY-MM-DD>/

A directory is created only when a gate has produced real evidence, in the same change that
produces it. No empty future gate directories.

Audio and baseline lanes use:

    evidence/AUDIO-L0-<YYYY-MM-DD>/
    evidence/AUDIO-L1-<YYYY-MM-DD>/
    evidence/AUDIO-L2-<YYYY-MM-DD>/
    evidence/S3-BASELINE-<YYYY-MM-DD>/

Tool output that reports success is not evidence. Evidence states what was actually inspected
and in what quantity.
