
# 📦 Trello Attachment Exporter

> **Effortlessly export and download all attachments from your Trello boards with preserved folder structure**

A Python script that automatically downloads all attachments from a Trello board export and organizes them into a clean folder structure, then packages everything into a convenient ZIP archive.

---

## ✨ Features

- 🔐 **Automatic Cookie Authentication** - Automatically detects Trello cookies from Chrome/Firefox
- 📂 **Organized Structure** - Creates folders matching your Trello board structure (Lists)
- 🏷️ **Smart File Naming** - Names files as `CardName_AttachmentName` for easy identification
 - 🏷️ **Smart File Naming** - Names files as `BoardName-CardName-OriginalFileName` (uses hyphens)
- 📦 **Auto-Zipping** - Packages everything into a ZIP file and cleans up
- 🍪 **Fallback Support** - Manual cookie configuration if auto-detection fails
- 🚀 **Batch Processing** - Downloads all attachments in one go

---

## 📋 Prerequisites

- Python 3.7+
- Required packages:
  ```bash
  pip install requests
  ```
- Active Trello account with browser session (Chrome or Firefox)
- Trello board JSON export

---

## 🚀 Quick Start

### 1️⃣ Export Your Trello Board

1. Open your Trello board
2. Go to **Menu** → **More** → **Print and Export** → **Export as JSON**
3. Save the `.json` file

### 2️⃣ Setup
1. Create an `Input/` folder next to the script and place the exported JSON there
2. Rename the file to `import_export.json` (so the path is `Input/import_export.json`)
3. The script will create an `Output/` folder next to the script for results

### 3️⃣ Configure Cookies (Optional)

If automatic cookie detection fails, manually add your Trello cookies in `trello_exporter.py`:
Instead of editing the script, you can create a `.env` file next to `trello_exporter.py` or copy `.sample.env` to `.env` and fill the values.

Example `.sample.env` entries (copy to `.env` and edit):

```env
# Trello cookie values (example keys)
cloud.session.token=YOUR_TOKEN_HERE
dsc=YOUR_DSC_TOKEN
aaId=YOUR_AAID_HERE
idMember=YOUR_MEMBER_ID_HERE
atl-bsc-consent-token=YOUR_CONSENT_TOKEN_HERE
```

**How to get cookies:**
1. Open Trello in your browser
2. Press `F12` (Developer Tools)
3. Go to **Application/Storage** → **Cookies** → `https://trello.com`
4. Copy the required cookie values

### 4️⃣ Run the Exporter

```bash
python trello_exporter.py
```

### 5️⃣ Get Your Files

Find your ZIP archive in the `Output/` folder! 📦

---

## 📁 Output Structure

After running the script, your files will be organized like this:

```
Output/
└── BoardName.zip
    └── BoardName/
        ├── List 1/
        │   ├── BoardName-CardName1-Attachment1.pdf
        │   ├── BoardName-CardName1-Attachment2.jpg
        │   └── BoardName-CardName2-Document.docx
        ├── List 2/
        │   ├── CardName3_Image.png
        │   └── CardName3_Spreadsheet.xlsx
        └── List 3/
            └── CardName4_Presentation.pptx
```

**Structure Breakdown:**
- **Root Level**: ZIP archive named after your board
- **Board Folder**: Contains all lists from your board
- **List Folders**: One folder for each Trello list
- **Files**: Named as `CardName_OriginalFileName` for easy identification
 - **Files**: Named as `BoardName-CardName-OriginalFileName` (hyphen-separated)

---

## 🔧 Troubleshooting

### ❌ "No cookies found" error

**Solution 1:** Make sure Chrome or Firefox is running with an active Trello session

**Solution 2:** Close your browser completely and run the script again

**Solution 3:** Use manual cookies (see Configuration section above)

### ❌ "File not found" error

- Ensure your JSON export is in the `TrelloJsonExport/` folder
- Rename it to `import_export.json`

### ❌ Download failures

- Check your internet connection
- Verify your Trello session is still active (not expired)
- Update manual cookies if needed

---

## 🛠️ Technical Details

**Last Updated:** February 15, 2026

**Supported Browsers:**
- Google Chrome
- Mozilla Firefox

**File Operations:**
- Downloads with authentication via cookies
- Sanitizes filenames (removes special characters)
- Creates ZIP archives with compression
- Auto-cleanup of temporary folders

---

## 📝 License

This project is provided as-is for personal use. Feel free to modify and distribute.

---

## 🤝 Contributing

Found a bug or want to contribute? Feel free to:
- Open an issue
- Submit a pull request
- Suggest improvements

---

## ⭐ Support

If this tool helped you, consider giving it a star! ⭐

---

**Made with ❤️ for the Trello community**

