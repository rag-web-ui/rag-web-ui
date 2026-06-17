# RADOCT - Quick Setup Guide

## What Was Done ✅
Your application now has complete RADOCT branding:
- **Logo Integration**: RADOCT logo + "Healthcare Platform" text on all pages
- **Color Scheme**: Consistent professional blue (#2563EB) and white
- **Pages Updated**: Home, Login, Register, Dashboard
- **Responsive Design**: Works perfectly on mobile, tablet, and desktop

---

## To Run on Your Local PC

### 1. Open PowerShell and go to your project
```powershell
cd C:\Users\ISSER TECH\Desktop\RADOCTV1\rag-web-ui
```

### 2. Pull latest changes
```powershell
git fetch origin
git pull origin main
```

### 3. Go to frontend folder
```powershell
cd frontend
```

### 4. Install dependencies (do this once)
```powershell
npm install
```

### 5. Start the development server
```powershell
npm run dev
```

### 6. Open in your browser
Visit these links:
- **Home**: http://localhost:3000
- **Login**: http://localhost:3000/login
- **Register**: http://localhost:3000/register
- **Dashboard**: http://localhost:3000/dashboard

---

## What You'll See

### Home Page
- Large RADOCT logo with "Healthcare Platform" text
- Blue buttons for "Commencer" and "Se Connecter"
- Professional layout with features section

### Login Page
- RADOCT logo at the top with name
- White form with blue accents
- Blue "Se connecter" button
- Link to register page

### Register Page
- Same layout as login
- Blue "Créer un Compte" button
- Form validation in place

### Dashboard
- RADOCT logo in sidebar header
- Blue "Healthcare Platform" subtitle
- Navigation menu with Knowledge Base, Chat, API Keys
- Professional blue and white theme throughout

---

## Color Reference

### Blue (Primary)
- **Uses**: Buttons, links, active items, titles
- **Hex**: #2563EB
- **Shade**: Professional blue

### White
- **Uses**: Backgrounds, cards
- **Hex**: #FFFFFF

### Light Blue (Hover States)
- **Uses**: Hover backgrounds, secondary items
- **Hex**: #BFDBFE

---

## File Changes Summary

| File | Change |
|------|--------|
| `dashboard-layout.tsx` | Added logo + "RADOCT Healthcare Platform" text |
| `login/page.tsx` | Added logo + "RADOCT Healthcare" text |
| `register/page.tsx` | Added logo + "RADOCT Healthcare" text |
| `page.tsx` (home) | Added logo with "RADOCT Healthcare Platform" |
| `globals.css` | Updated colors to blue/white scheme |

---

## Troubleshooting

### Dev server won't start
```powershell
# Try clearing cache
Remove-Item -Recurse -Force .next
npm run dev
```

### Logo not showing
- Make sure `/frontend/public/doctome-logo.png` exists
- If not, ask me to copy it there

### Colors look wrong
- Press Ctrl+Shift+R to hard refresh browser
- Or clear browser cache

### Changes not appearing
```powershell
# Stop the server (Ctrl+C)
# Then restart:
npm run dev
```

---

## Next Steps

1. ✅ **Pull and run** the code locally
2. ✅ **Test all pages** to verify styling
3. ⏳ (Optional) **Deploy** to production when ready
4. ⏳ (Optional) **Customize** colors or logo if needed

---

## Documentation

For complete implementation details, see:
📄 **`RADOCT_BRANDING_IMPLEMENTATION.md`** - Full technical documentation

---

## Summary

Your RADOCT Healthcare Platform is ready! 🎉

- ✅ Logo on all pages
- ✅ Professional blue and white colors
- ✅ Responsive mobile design
- ✅ Complete branding implementation

Just pull, install, and run!

```powershell
cd frontend
npm install
npm run dev
```

Then visit `http://localhost:3000` to see your branded platform.

