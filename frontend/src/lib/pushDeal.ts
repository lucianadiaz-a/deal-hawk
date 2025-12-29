/**
 * Push Deal payload builder for Wizard-of-Oz simulation.
 * Generates formatted deal payloads matching the example format.
 */

export interface PushDealInput {
  productName: string;
  retailerName: string;
  priceCents?: number | null;
  storeUrl?: string | null;
}

export interface PushDealPayload {
  title: string;
  text: string;
  priceCents: number;
  commissionCents: number;
  totalCents: number;
}

// Fixed shipping addresses (from examples)
const SHIP_TO_LOCATIONS = [
  '123 Commerce St, Wilmington, DE 19801',
  '456 Business Ave, Dover, DE 19901',
  '789 Trade Blvd, Newark, DE 19711',
];

/**
 * Generate a deterministic hash from a string (simple implementation)
 */
function simpleHash(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash);
}

/**
 * Generate a dummy deal link based on product name
 */
function generateDealLink(productName: string): string {
  const hash = simpleHash(productName);
  const encoded = encodeURIComponent(productName.toLowerCase().replace(/\s+/g, '-'));
  return `https://mbg.deals/${encoded}-${hash.toString(36)}`;
}

/**
 * Generate a dummy store link if not provided
 */
function generateStoreLink(retailerName: string, productName: string): string {
  // If we have a store URL, use it
  // Otherwise generate a realistic dummy URL
  const retailerLower = retailerName.toLowerCase().replace(/\s+/g, '');
  if (retailerLower.includes('amazon')) {
    const hash = simpleHash(productName);
    return `https://www.amazon.com/dp/B${hash.toString().slice(0, 9).padStart(9, '0')}`;
  } else if (retailerLower.includes('bestbuy')) {
    const hash = simpleHash(productName);
    return `https://www.bestbuy.com/site/${productName.toLowerCase().replace(/\s+/g, '-')}/${hash}.p`;
  } else if (retailerLower.includes('target')) {
    const hash = simpleHash(productName);
    return `https://www.target.com/p/${productName.toLowerCase().replace(/\s+/g, '-')}/-/${hash}`;
  }
  // Generic fallback
  return `https://www.${retailerName.toLowerCase().replace(/\s+/g, '')}.com/product/${simpleHash(productName)}`;
}

/**
 * Calculate commission based on price
 * - 5-7% for items < $100
 * - 3-5% for items >= $100
 */
function calculateCommission(priceCents: number): number {
  const priceDollars = priceCents / 100;
  if (priceDollars < 100) {
    // 5-7% for small items
    const pct = 5 + (simpleHash(priceCents.toString()) % 3); // 5, 6, or 7%
    return Math.round(priceCents * pct / 100);
  } else {
    // 3-5% for expensive items
    const pct = 3 + (simpleHash(priceCents.toString()) % 3); // 3, 4, or 5%
    return Math.round(priceCents * pct / 100);
  }
}

/**
 * Extract variant/color from product name if present, otherwise use a default
 */
function extractVariant(productName: string): string {
  // Try to extract common variant patterns
  const variantPatterns = [
    /\(([^)]+)\)/g,  // Text in parentheses
    /- ([A-Z][a-z]+(?: [A-Z][a-z]+)*)$/,  // Dash-separated variant at end
    /\d+GB/i,  // Storage size
    /\d+mm/i,  // Size in mm
  ];

  for (const pattern of variantPatterns) {
    const match = productName.match(pattern);
    if (match) {
      return match[0].replace(/[()]/g, '').trim();
    }
  }

  // Default: use a simple hash-based variant
  const hash = simpleHash(productName);
  const variants = ['Black', 'White', 'Silver', 'Space Gray', 'Blue'];
  return variants[hash % variants.length];
}

/**
 * Build a formatted push deal payload
 */
export function buildPushDealPayload(input: PushDealInput): PushDealPayload {
  const {
    productName,
    retailerName,
    priceCents: inputPriceCents,
    storeUrl,
  } = input;

  // Use provided price or generate a reasonable dummy
  const priceCents = inputPriceCents ?? 9999; // Default $99.99 if not provided

  // Calculate commission and total
  const commissionCents = calculateCommission(priceCents);
  const totalCents = priceCents + commissionCents;

  // Format prices
  const priceDollars = (priceCents / 100).toFixed(2);
  const commissionDollars = (commissionCents / 100).toFixed(2);
  const totalDollars = (totalCents / 100).toFixed(2);

  // Extract variant
  const variant = extractVariant(productName);

  // Generate links
  const dealLink = generateDealLink(productName);
  const finalStoreUrl = storeUrl || generateStoreLink(retailerName, productName);

  // Build formatted text payload
  const lines = [
    `ACTIVE DEAL: ${productName} - ${variant}`,
    `STORE LINK: ${finalStoreUrl}`,
    `DEAL LINK: ${dealLink}`,
    `PRICE: $${priceDollars}`,
    `COMMISSION: $${commissionDollars}`,
    `TOTAL: $${totalDollars}`,
    `DELIVERY: DROP OFF,SHIP DIRECT`,
    `STORE: ${retailerName}`,
    `SPECIFICATIONS: ON SALE NOW, COMMITMENT REQUIRED`,
    `SHIP TO LOCATION 1: ${SHIP_TO_LOCATIONS[0]}`,
    `SHIP TO LOCATION 2: ${SHIP_TO_LOCATIONS[1]}`,
    `SHIP TO LOCATION 3: ${SHIP_TO_LOCATIONS[2]}`,
    ``,
    `For orders shipped to DE, please upload tracking information promptly and include the three-letter identifier 'MBG' in the name field. We cannot guarantee item retrieval or accept responsibility for tracking uploads beyond 7 days after delivery.`,
  ];

  const text = lines.join('\n');
  const title = `${productName} - ${variant}`;

  return {
    title,
    text,
    priceCents,
    commissionCents,
    totalCents,
  };
}

