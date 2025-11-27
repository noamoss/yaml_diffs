/** Utility to extract sections from YAML documents by marker path. */

/**
 * Extract a section from a parsed YAML object by following a marker path.
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

/**
 * Extract and serialize a section from YAML text by marker path.
 *
 * @param yamlText - The full YAML document as a string
 * @param markerPath - Array of markers representing the path to the section
 * @returns Promise resolving to the section as a YAML string, or null if not found
 */
export async function extractSectionYaml(
  yamlText: string,
  markerPath: string[] | null
): Promise<string | null> {
  if (!markerPath || markerPath.length === 0 || !yamlText) {
    return null;
  }

  try {
    // Parse YAML
    const yamlModule = await import("js-yaml");
    const yaml = (yamlModule as any).default || yamlModule;
    const doc = yaml.load(yamlText);

    // Find the section
    const section = findSectionInDocument(doc, markerPath);
    if (!section) {
      return null;
    }

    // Serialize back to YAML
    return yaml.dump(section, {
      indent: 2,
      lineWidth: -1, // No line wrapping
      quotingType: '"',
      forceQuotes: false,
    });
  } catch (error) {
    console.error("Error extracting section YAML:", error);
    return null;
  }
}
