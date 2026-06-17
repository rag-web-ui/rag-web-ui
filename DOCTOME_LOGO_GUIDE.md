# DOCTOME Logo Integration Guide

## Overview
This guide explains how to properly extract and integrate the DOCTOME healthcare branding logo into your application.

## Current Implementation
The application has been redesigned with the DOCTOME healthcare branding:
- **Logo File**: `/frontend/public/doctome-logo.png`
- **Branding**: Professional healthcare/medical clinic theme
- **Color Scheme**: 
  - Primary Blue: `#0052CC` (RGB: 0, 82, 204)
  - White: Background
  - Green Accent: Medical/health indicator

## Logo Integration Points

### 1. **Login Page** (`/src/app/login/page.tsx`)
```tsx
<img
  src="/doctome-logo.png"
  alt="DOCTOME Logo"
  className="h-16 w-auto mx-auto mb-4"
/>
```
- Displays at the top of the login form
- 64px height with auto width for proportional scaling
- Centered on the page

### 2. **Register Page** (`/src/app/register/page.tsx`)
```tsx
<img
  src="/doctome-logo.png"
  alt="DOCTOME Logo"
  className="h-16 w-auto mx-auto mb-4"
/>
```
- Same implementation as login page for consistent branding

### 3. **Home Page** (`/src/app/page.tsx`)
```tsx
<img
  src="/doctome-logo.png"
  alt="DOCTOME"
  className="h-24 mx-auto mb-8"
/>
```
- Larger display (96px) for hero section
- Creates visual impact on landing page

### 4. **Dashboard** (`/src/components/layout/dashboard-layout.tsx`)
```tsx
<img
  src="/doctome-logo.png"
  alt="DOCTOME Logo"
  className="h-12 w-auto"
/>
<span className="text-blue-900 font-bold tracking-wide">DOCTOME</span>
```
- Sidebar header logo integration
- Professional display with brand name text

## How to Replace or Update the Logo

### Option A: Using Generated Logo
The current logo was automatically generated and is stored at `/frontend/public/doctome-logo.png`.

### Option B: Using Your Own Logo
1. **Prepare Your Logo**:
   - Format: PNG with transparent background (recommended)
   - Minimum size: 200x200px
   - Maximum size: 1000x1000px
   - File size: < 100KB

2. **Upload Your Logo**:
   - Replace the file at `/frontend/public/doctome-logo.png`
   - OR upload to a new filename and update all image sources

3. **Update References**:
   - Change `src="/doctome-logo.png"` to your new filename in:
     - `/src/app/login/page.tsx`
     - `/src/app/register/page.tsx`
     - `/src/app/page.tsx`
     - `/src/components/layout/dashboard-layout.tsx`

### Option C: Extracting from Existing Image
If you have the DOCTOME logo in another image format or need to extract it:

1. **Use Image Editing Software**:
   - Open the source image in Photoshop, GIMP, or similar
   - Use the "Select" or "Magic Wand" tool to isolate the logo
   - Create a transparent background layer
   - Export as PNG

2. **Using Online Tools**:
   - Visit: https://remove.bg (for removing backgrounds)
   - Upload your image
   - Download as PNG
   - Save to `/frontend/public/doctome-logo.png`

3. **Using Command Line** (if you have the image):
   ```bash
   # Using ImageMagick
   convert source-image.jpg -transparent white -trim doctome-logo.png
   
   # Or using GraphicsMagick
   gm convert source-image.jpg -transparent white doctome-logo.png
   ```

## Design Specifications

### Logo Dimensions by Context
| Page | Size | Usage |
|------|------|-------|
| Login/Register Forms | 64px (h-16) | Top of form |
| Home Page Hero | 96px (h-24) | Main header |
| Dashboard Sidebar | 48px (h-12) | Navigation header |

### Color Usage
- **Primary Blue**: Used for buttons, active states, and branding
- **White**: Background and text on blue
- **Gray**: Secondary text (placeholder, disabled)
- **Green Accent**: Medical/health indicators (logo element)

## Responsive Considerations
- Logos scale automatically with `w-auto` for proper aspect ratio
- Heights are fixed with Tailwind classes (h-16, h-24, h-12)
- Mobile-friendly due to automatic width scaling

## Accessibility
- All images have proper `alt` attributes describing the logo
- DOCTOME brand name is also displayed as text in sidebar for redundancy
- High contrast between logo and backgrounds

## Browser Compatibility
- PNG format with transparency is supported in all modern browsers
- SVG version can be created for better scalability if needed

## Future Enhancements
- Consider creating SVG version for infinite scalability
- Add dark mode logo variant if dark theme is implemented
- Create favico version for browser tab
- Generate multiple DPI versions for high-resolution displays

## Support
For logo replacement or additional branding needs, ensure:
1. Logo files are in `/frontend/public/` directory
2. All references are updated across all pages
3. Responsive sizes are maintained for different contexts
4. Accessibility standards are preserved
