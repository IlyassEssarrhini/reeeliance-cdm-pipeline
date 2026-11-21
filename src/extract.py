import csv
import logging

logger = logging.getLogger(__name__)

def read_csv_records(path: str) -> list[dict]:
    """Liest eine CSV-Datei und gibt eine Liste von Dicts zurück (eine pro Zeile).
    Zeilen, die auf zwei physische zeile verteilt sind, werden zusammengeführt und die Reparatur wird geloggt.
    """

    # First: Datei lesen
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()


    # Second: header und erwartete Spaltenzahl
    header = lines[0]
    expected = len(header.split(","))

    # Third: Zeile reparieren
    repaired = []
    buffer = ""
    for line_no, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue # leere Zeile an buffer anhängen

        buffer = buffer + line
        if len(buffer.split(",")) >= expected:
            repaired.append(buffer)
            buffer = ""
        else:
            logger.warning("Line %s hat too few fileds, merging with next line", line_no)

    # Unvollstaendiger Datensatz am Dateiende
    if buffer:
        logger.error("Incomplete record at end of the file dropped: %r", buffer)

    # Fourth: In Dicts umwandeln
    reader = csv.DictReader([header] + repaired)
    records = list(reader)

    logger.info("Read %s records fro  %s", len(records), path)
    return records