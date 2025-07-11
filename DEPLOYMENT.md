# Deployment Guide - Race Condition Security Tool

This guide will help you deploy the Race Condition Security Tool to Vercel for testing and public access.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)
3. **Vercel CLI** (optional): `npm i -g vercel`

## Files Structure

Ensure your project has these files:

```
race-condition-tool/
├── app.py                 # Flask application
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
├── race_condition_detector.py  # Core detection engine
├── templates/
│   └── index.html       # Web interface
└── README.md
```

## Deployment Steps

### Method 1: Vercel Dashboard (Recommended)

1. **Push to Git Repository**
   ```bash
   git add .
   git commit -m "Add race condition security tool"
   git push origin main
   ```

2. **Connect to Vercel**
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your Git repository
   - Vercel will auto-detect it's a Python project

3. **Configure Build Settings**
   - **Framework Preset**: Other
   - **Build Command**: `pip install -r requirements.txt`
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

4. **Environment Variables** (if needed)
   - Add any environment variables in the Vercel dashboard

5. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Your app will be available at `https://your-project.vercel.app`

### Method 2: Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel
   ```

4. **Follow the prompts**
   - Link to existing project or create new
   - Confirm deployment settings
   - Wait for deployment

## Configuration Details

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

### requirements.txt
```
Flask==2.3.3
Werkzeug==2.3.7
```

## Testing the Deployment

1. **Health Check**
   - Visit `https://your-app.vercel.app/health`
   - Should return: `{"status": "healthy", "service": "Race Condition Security Tool"}`

2. **Main Interface**
   - Visit `https://your-app.vercel.app/`
   - Should show the web interface

3. **API Endpoints**
   - `/api/scan` - File upload scanning
   - `/api/scan-text` - Text content scanning
   - `/api/examples` - Get example code

## Features Available

✅ **File Upload**: Drag & drop or browse files  
✅ **Code Editor**: Paste code directly  
✅ **Multiple Languages**: Python, JS, TS, Java, C++, C, Go, Rust  
✅ **Real-time Analysis**: Instant race condition detection  
✅ **Detailed Reports**: Severity levels and recommendations  
✅ **Example Library**: Pre-built test cases  
✅ **Responsive Design**: Works on mobile and desktop  

## Troubleshooting

### Common Issues

1. **Build Fails**
   - Check `requirements.txt` has correct dependencies
   - Ensure all files are committed to Git
   - Check Vercel logs for specific errors

2. **App Not Loading**
   - Verify `app.py` has correct Flask setup
   - Check `vercel.json` configuration
   - Ensure `templates/` folder exists

3. **Import Errors**
   - Make sure `race_condition_detector.py` is in the root directory
   - Check all imports in `app.py`

### Debugging

1. **Check Vercel Logs**
   - Go to your project dashboard
   - Click on the latest deployment
   - Check "Functions" tab for errors

2. **Local Testing**
   ```bash
   pip install -r requirements.txt
   python app.py
   ```
   - Test locally before deploying

3. **Environment Variables**
   - Add `FLASK_ENV=production` if needed
   - Check for any missing environment variables

## Security Considerations

⚠️ **Important**: This tool analyzes code for security vulnerabilities. Consider:

1. **File Size Limits**: Set appropriate limits for uploaded files
2. **Rate Limiting**: Implement to prevent abuse
3. **Input Validation**: Validate all uploaded content
4. **Temporary Files**: Ensure proper cleanup
5. **Error Handling**: Don't expose sensitive information

## Performance Optimization

1. **File Processing**: Implement async processing for large files
2. **Caching**: Cache common patterns and results
3. **CDN**: Use Vercel's CDN for static assets
4. **Database**: Consider adding database for result storage

## Monitoring

1. **Vercel Analytics**: Monitor usage and performance
2. **Error Tracking**: Set up error monitoring
3. **Uptime Monitoring**: Ensure service availability
4. **Usage Metrics**: Track API usage and file uploads

## Customization

### Adding New Languages
1. Update `app.py` language mapping
2. Add detection patterns in `race_condition_detector.py`
3. Update frontend language selector

### Adding New Detection Types
1. Add patterns to `RaceConditionDetector.patterns`
2. Implement detection method
3. Update frontend to display new types

### Styling Changes
1. Modify `templates/index.html` CSS
2. Update color scheme and layout
3. Test responsive design

## Support

For issues with:
- **Vercel Deployment**: Check Vercel documentation
- **Flask Application**: Check Flask documentation
- **Race Condition Detection**: Review the core detector code
- **Web Interface**: Check browser console for errors

## Next Steps

After successful deployment:

1. **Share the URL** with your team
2. **Test with real code** from your projects
3. **Gather feedback** and iterate
4. **Add more features** as needed
5. **Monitor usage** and performance

Your Race Condition Security Tool is now ready for public testing! 🚀 