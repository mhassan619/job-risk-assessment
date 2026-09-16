/**
 * @fileoverview Curated Evaluation Presets & Standardized Threat Vectors
 */

export const PRESET_VECTORS = Object.freeze({
  SUSPICIOUS: {
    id: 'suspicious_demo',
    title: 'Suspicious Job Example',
    subtitle: 'Upfront fee + unrealistic salary',
    content: "URGENT HIRING! Data Entry Clerk needed immediately, no experience required. Earn $8,000/month working from home. Limited positions available — apply today! To secure your spot, a one-time $150 registration and training fee is required before we can process your onboarding. Please send payment details and a copy of your ID to confirm your position.",
    recruiterEmail: 'recruitment-desk@gmail.com',
    jobUrl: 'http://careers-portal-onboarding.xyz'
  },
  NORMAL: {
    id: 'normal_demo',
    title: 'Normal Job Example',
    subtitle: 'Clear role + realistic requirements',
    content: "Software Engineer Intern — ABC Technologies\n\nWe're looking for a motivated intern to join our platform team for a 12-week summer program. You'll work alongside senior engineers on real features, participate in code reviews, and ship production code.\n\nRequirements: familiarity with Python or JavaScript, coursework in data structures, strong communication skills. Compensation is hourly and disclosed during the interview process.",
    recruiterEmail: 'talent@abctechnologies.com',
    jobUrl: 'https://abctechnologies.com/careers'
  }
});
