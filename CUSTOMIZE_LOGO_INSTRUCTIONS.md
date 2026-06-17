# How to Customize the DOCTOME Logo

## Quick Start Guide

The DOCTOME application now displays a professional healthcare logo throughout the interface. This guide explains how to replace it with your own custom logo.

---

## Current Logo Location

**File Path**: `/frontend/public/doctome-logo.png`

The logo is currently displayed in 4 locations:
1. 📱 Login Page (`/src/app/login/page.tsx`)
2. 📝 Register Page (`/src/app/register/page.tsx`)
3. 🏠 Home Page (`/src/app/page.tsx`)
4. 📊 Dashboard Sidebar (`/src/components/layout/dashboard-layout.tsx`)

---

## Option 1: Extract Logo from Image (Recommended)

### If you have the DOCTOME logo in an image file:

#### Method A: Online Background Remover
**Easiest method - No software installation needed**

1. Visit: [remove.bg](https://remove.bg)
2. Click "Upload Image"
3. Select your image with the DOCTOME logo
4. Wait for processing (automatic background removal)
5. Click "Download" to get PNG version
6. Save the file as `doctome-logo.png`

#### Method B: Using GIMP (Free Software)
1. Download GIMP: [gimp.org](https://www.gimp.org/)
2. Open your image in GIMP
3. Select "Layer" → "Transparency" → "Add Alpha Channel"
4. Use "Select by Color" tool (magic wand) to select background
5. Press Delete to remove background
6. File → Export As → Save as `doctome-logo.png` (PNG format)
7. Uncheck "Interlacing" if asked, click Export

#### Method C: Using Photoshop
1. Open image in Photoshop
2. Select "Object Selection Tool" (top toolbar)
3. Click the logo to auto-select it
4. Right-click → "Select Subject"
5. Select → Inverse (to select background)
6. Delete the background
7. File → Export As → Choose PNG format
8. Save as `doctome-logo.png`

#### Method D: Command Line (Linux/Mac)
```bash
# Using ImageMagick
convert your-image.jpg -fuzz 20% -transparent white doctome-logo.png

# Using GraphicsMagick
gm convert your-image.jpg -transparent white doctome-logo.png

# Using GIMP in batch mode
gimp -i -b '(let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "input.jpg" "input.jpg"))) (drawable (car (gimp-image-get-active-layer image)))) (gimp-context-set-background '(255 255 255)) (gimp-drawable-edit-clear drawable) (gimp-file-save RUN-NONINTERACTIVE image drawable "output.png" "output.png") (gimp-image-delete image))' -b '(gimp-quit 0)'
```

---

## Option 2: Create a New Logo

### If you want to design a custom DOCTOME logo:

#### Quick Design Ideas
- **Medical Cross**: Blue plus sign with green leaf (health indicator)
- **Stethoscope**: Professional healthcare symbol
- **Caduceus**: Medical staff symbol
- **Plus Sign with Heart**: Medical + patient care
- **Shield with Cross**: Security + healthcare

#### Design Tools (Free)
1. **Canva** (canva.com)
   - Templates available for healthcare logos
   - Drag-and-drop interface
   - Free tier available
   - Download as PNG

2. **Figma** (figma.com)
   - Professional design tool
   - Free tier available
   - Community templates
   - Export to PNG

3. **Adobe Express** (express.adobe.com)
   - Free Adobe tool
   - Logo maker available
   - PNG export

4. **Inkscape** (inkscape.org)
   - Free vector graphics software
   - Create scalable logos
   - Export as PNG

#### Design Specifications
- **Recommended Size**: 500x500px (minimum 200x200px)
- **Format**: PNG with transparent background
- **File Size**: Keep under 100KB for fast loading
- **Colors**: 
  - Primary: Blue (#0052CC)
  - Accent: Green (for health element)
  - White text/background safe

---

## Option 3: Use an Existing Logo Template

### Free Logo Resources

1. **Freepik** (freepik.com)
   - Healthcare/medical logos
   - Download premium versions or free alternatives
   - PNG format available

2. **Flaticon** (flaticon.com)
   - Medical symbols and logos
   - Customizable colors
   - PNG export

3. **LogoMakr** (logomakr.com)
   - Healthcare logo templates
   - Free logo maker
   - PNG download

4. **Looka** (looka.com)
   - AI logo generator
   - Free trial available
   - Customizable results

---

## Replace the Logo

### Step-by-Step Replacement

#### 1. Prepare Your Logo File
- Format: PNG (with transparent background preferred)
- Filename: `doctome-logo.png`
- Size: 500x500px recommended
- File size: < 100KB

#### 2. Place Logo File
Navigate to your project folder and save the file:
```
/vercel/share/v0-project/frontend/public/doctome-logo.png
```

**Via File Explorer**:
1. Open file explorer
2. Navigate to: `frontend/public/`
3. Replace or upload `doctome-logo.png`

**Via Command Line**:
```bash
cp your-custom-logo.png /vercel/share/v0-project/frontend/public/doctome-logo.png
```

#### 3. Verify the Replace
- Refresh your browser (Ctrl+R or Cmd+R)
- Hard refresh to clear cache (Ctrl+Shift+R or Cmd+Shift+R)
- Check all 4 pages:
  - Login: http://localhost:3000/login
  - Register: http://localhost:3000/register
  - Home: http://localhost:3000
  - Dashboard: http://localhost:3000/dashboard

---

## Adjust Logo Display Size (Optional)

The logo appears in different sizes on different pages. You can adjust them by editing these files:

### Login Page (64px)
**File**: `/frontend/src/app/login/page.tsx`

Find this line:
```tsx
<img
  src="/doctome-logo.png"
  alt="DOCTOME Logo"
  className="h-16 w-auto mx-auto mb-4"
/>
```

Change `h-16` to:
- `h-12` for smaller (48px)
- `h-20` for larger (80px)
- `h-24` for extra large (96px)

### Register Page (64px)
**File**: `/frontend/src/app/register/page.tsx`

Same as login - find and modify the `h-16` class

### Home Page (96px)
**File**: `/frontend/src/app/page.tsx`

Find this line and modify `h-24`:
- `h-20` for smaller (80px)
- `h-32` for larger (128px)

### Dashboard (48px)
**File**: `/frontend/src/components/layout/dashboard-layout.tsx`

Find this line and modify `h-12`:
- `h-8` for smaller (32px)
- `h-16` for larger (64px)

**Tailwind Size Reference**:
```
h-8  = 32px
h-12 = 48px
h-16 = 64px
h-20 = 80px
h-24 = 96px
h-32 = 128px
```

---

## Troubleshooting

### Logo Not Appearing
1. **Clear browser cache**: 
   - Press Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)
   - Select "All time"
   - Check "Images and files"
   - Click Clear

2. **Check file path**:
   - Ensure file is at: `/frontend/public/doctome-logo.png`
   - Check file name spelling (case-sensitive on Linux)

3. **Verify file format**:
   - Must be PNG or JPG
   - Check file isn't corrupted (open in image viewer)

4. **Restart dev server**:
   - Stop the development server
   - Delete `.next` folder
   - Restart: `npm run dev`

### Logo Looks Blurry
- Increase original image resolution (use 1000x1000px minimum)
- Logo size might be too large - reduce `h-*` class
- Ensure original image is clear

### Logo Has Wrong Aspect Ratio
- Original image aspect ratio is preserved
- Use `h-*` classes without width restrictions
- Alternatively, use `max-w-*` to limit width

### Background Not Transparent
- Re-export logo as PNG (not JPG)
- Use remove.bg to automatically remove background
- Or manually remove in GIMP/Photoshop

---

## Advanced: Change Logo Across All Pages

If you want to use a different filename than `doctome-logo.png`:

1. Save your logo as: `/frontend/public/your-logo-name.png`
2. Edit these 4 files to change the `src` attribute:

**File 1**: `/frontend/src/app/login/page.tsx`
```tsx
// Change from:
src="/doctome-logo.png"
// To:
src="/your-logo-name.png"
```

**File 2**: `/frontend/src/app/register/page.tsx`
```tsx
src="/your-logo-name.png"
```

**File 3**: `/frontend/src/app/page.tsx`
```tsx
src="/your-logo-name.png"
```

**File 4**: `/frontend/src/components/layout/dashboard-layout.tsx`
```tsx
src="/your-logo-name.png"
```

---

## Logo Best Practices

### Design Principles
✅ **DO**:
- Use blue and white colors (matches app theme)
- Keep it simple and recognizable
- Use high resolution (500x500px minimum)
- Test on all page sizes (mobile, tablet, desktop)
- Ensure good contrast on backgrounds
- Include your brand name in the design

❌ **DON'T**:
- Use too many colors (stick to 2-3)
- Make text too small
- Use very compressed/low quality images
- Forget transparent background
- Use logos with cluttered designs
- Make file size too large

### File Format
- **PNG**: Best choice (supports transparency)
- **SVG**: Professional option (infinitely scalable)
- **JPG**: Not recommended (no transparency support)
- **WebP**: Modern format (ensure browser support)

---

## Need Help?

### Common Questions

**Q: Can I use an SVG logo instead?**
A: Yes! Save as `.svg` file in `/frontend/public/` and update the `src` attribute in all 4 files.

**Q: Will changing the logo break anything?**
A: No, just ensure it's named correctly and references are updated.

**Q: Can I use an animated logo?**
A: Yes, for GIF or animated SVG, but keep file size small.

**Q: What if my logo has a colored background?**
A: Use remove.bg or GIMP to make the background transparent first.

**Q: How do I revert to the original logo?**
A: Keep a backup of the original `doctome-logo.png` before replacing it.

---

## Summary Checklist

- [ ] Logo file prepared (PNG format, transparent background)
- [ ] Logo saved to `/frontend/public/doctome-logo.png`
- [ ] Browser cache cleared
- [ ] Dev server restarted
- [ ] Logo appears on all 4 pages
- [ ] Logo size looks appropriate
- [ ] Logo displays on mobile/tablet/desktop
- [ ] No console errors in browser

**All done!** Your custom DOCTOME logo is now integrated into the application. 🎉
