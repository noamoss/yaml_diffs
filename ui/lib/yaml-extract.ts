/** Utility functions for working with YAML documents in the UI.
 *
 * Note: Section extraction and line number finding are now handled by the backend API.
 * This file contains only UI-specific utilities that may be needed for client-side operations.
 */

/**
 * Extract a section from a parsed YAML object by following a marker path.
 * This is a UI-only utility for client-side YAML manipulation if needed.
 *
 * @param doc - The parsed YAML document object
 * @param markerPath - Array of markers representing the path to the section
 * @returns The section object, or null if not found
 */
export function findSectionInDocument(
  doc: any,
  markerPath: string[]
): any | null {
  if (!doc || !doc.document || !doc.document.sections) {
    return null;
  }

  let currentSections = doc.document.sections;
  let currentPath = [...markerPath];

  // Navigate through the marker path
  while (currentPath.length > 0) {
    const targetMarker = currentPath.shift()!;
    const foundSection = currentSections.find(
      (section: any) => section.marker === targetMarker
    );

    if (!foundSection) {
      return null;
    }

    // If we've reached the end of the path, return this section
    if (currentPath.length === 0) {
      return foundSection;
    }

    // Otherwise, continue navigating into nested sections
    if (!foundSection.sections || foundSection.sections.length === 0) {
      return null; // Path continues but no nested sections
    }

    currentSections = foundSection.sections;
  }

  return null;
}

/**
 * Convert a section object back to YAML string.
 * Uses js-yaml for serialization.
 * This is a UI-only utility for client-side YAML manipulation if needed.
 *
 * @param section - The section object to serialize
 * @returns YAML string representation
 */
export async function sectionToYaml(section: any): Promise<string | null> {
  if (!section) {
    return null;
  }

  try {
    // Dynamic import for js-yaml
    const yamlModule = await import("js-yaml");
    const yaml = (yamlModule as any).default || yamlModule;
    return yaml.dump(section, {
      indent: 2,
      lineWidth: -1, // No line wrapping
      quotingType: '"',
      forceQuotes: false,
    });
  } catch (error) {
    console.error("Error serializing section to YAML:", error);
    return null;
  }
}
