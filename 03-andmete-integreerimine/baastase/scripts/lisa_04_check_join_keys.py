"""Abifunktsioonid ühendusvõtmete sobivuse kontrolliks."""


def build_normalized_key_set(values, normalize_key):
    """Tagasta hulk puhastatud võtmetest.

    Kasutame sama normaliseerimisreeglit, mida ETL kasutab ühendamisel.
    Nii käituvad kontroll ja päris ühendamine ühtemoodi.
    """

    normalized_keys = set()

    for value in values:
        normalized_value = normalize_key(value)
        if normalized_value is not None:
            normalized_keys.add(normalized_value)

    return normalized_keys


def compare_source_keys(left_values, right_values, normalize_key):
    """Tagasta ülevaade kahe võtmehulgaga võrdlusest."""

    left_keys = build_normalized_key_set(left_values, normalize_key)
    right_keys = build_normalized_key_set(right_values, normalize_key)

    return {
        "matched_keys": sorted(left_keys & right_keys),
        "left_only_keys": sorted(left_keys - right_keys),
        "right_only_keys": sorted(right_keys - left_keys),
    }


def print_source_key_report(
    left_values,
    right_values,
    normalize_key,
    left_label,
    right_label,
):
    """Prindi lühike raport kahe allika võtmete sobitumise kohta."""

    comparison = compare_source_keys(
        left_values=left_values,
        right_values=right_values,
        normalize_key=normalize_key,
    )

    print(f"- Sobitunud e-posti võtmeid: {len(comparison['matched_keys'])}")
    print(
        f"- {left_label} poolel ilma {right_label} vasteta: "
        f"{len(comparison['left_only_keys'])}"
    )
    for key in comparison["left_only_keys"]:
        print(f"  {left_label} ainult: {key}")

    print(
        f"- {right_label} poolel ilma {left_label} vasteta: "
        f"{len(comparison['right_only_keys'])}"
    )
    for key in comparison["right_only_keys"]:
        print(f"  {right_label} ainult: {key}")


def print_key_check_report(api_users, status_lookup, normalize_key):
    """Prindi põhiraja raport API ja CSV võtmete sobitumise kohta."""

    print_source_key_report(
        left_values=(user["email"] for user in api_users),
        right_values=status_lookup.keys(),
        normalize_key=normalize_key,
        left_label="API",
        right_label="CSV",
    )


def print_three_source_key_report(
    api_users,
    status_lookup,
    preferences,
    normalize_key,
):
    """Prindi raport kolme allika võtmete sobitumise kohta."""

    print("Võrdlus 1: API ja CSV")
    print_source_key_report(
        left_values=(user["email"] for user in api_users),
        right_values=status_lookup.keys(),
        normalize_key=normalize_key,
        left_label="API",
        right_label="CSV",
    )

    print("Võrdlus 2: API ja JSON")
    print_source_key_report(
        left_values=(user["email"] for user in api_users),
        right_values=(item["email"] for item in preferences),
        normalize_key=normalize_key,
        left_label="API",
        right_label="JSON",
    )
