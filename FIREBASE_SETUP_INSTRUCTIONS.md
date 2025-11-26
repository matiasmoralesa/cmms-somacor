# Firebase Setup Instructions

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or select existing project
3. Enter project name (e.g., "cmms-production")
4. Enable Google Analytics (optional)
5. Click "Create project"

## Step 2: Enable Firebase Authentication

1. In Firebase Console, go to "Build" → "Authentication"
2. Click "Get started"
3. Go to "Sign-in method" tab
4. Enable "Email/Password" provider
5. Click "Save"

## Step 3: Get Firebase Configuration for Frontend

1. In Firebase Console, go to Project Settings (gear icon)
2. Scroll down to "Your apps" section
3. Click the web icon (</>) to add a web app
4. Register app with nickname (e.g., "CMMS Web App")
5. Copy the Firebase configuration object:

```javascript
const firebaseConfig = {
  apiKey: "AIza...",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc123"
};
```

6. Add these values to `frontend/.env`:

```bash
VITE_API_URL=http://localhost:8000/api/v1
VITE_FIREBASE_API_KEY=AIza...
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abc123
```

## Step 4: Generate Service Account Key for Backend

1. In Firebase Console, go to Project Settings → Service accounts
2. Click "Generate new private key"
3. Click "Generate key" - this downloads a JSON file
4. Save the JSON file securely (e.g., `firebase-service-account.json`)
5. **IMPORTANT**: Never commit this file to version control!
6. Add to `.gitignore`:

```
# Firebase credentials
firebase-service-account.json
*-firebase-*.json
```

7. Update `backend/.env`:

```bash
FIREBASE_CREDENTIALS_PATH=/absolute/path/to/firebase-service-account.json
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
```

## Step 5: Configure Firebase for Production

### For Google Cloud Run (Backend)

1. Upload service account JSON to Google Cloud Storage or Secret Manager
2. Set environment variable in Cloud Run:
   - `FIREBASE_CREDENTIALS_PATH`: Path to mounted secret or use Secret Manager
   - Or use Application Default Credentials (ADC) if using same GCP project

### For Frontend (Static Hosting)

1. Firebase config can be public (it's safe to expose)
2. Add environment variables to your hosting platform:
   - Vercel: Add to Environment Variables
   - Netlify: Add to Build environment variables
   - Firebase Hosting: Use `.env.production`

## Step 6: Verify Setup

### Backend Verification

```python
# Test Firebase Admin SDK initialization
from firebase_admin import credentials, initialize_app, auth

cred = credentials.Certificate('path/to/service-account.json')
initialize_app(cred)

# Test creating a user
user = auth.create_user(
    email='test@example.com',
    password='testpass123'
)
print(f"Created user: {user.uid}")
```

### Frontend Verification

```typescript
// Test Firebase SDK initialization
import { initializeApp } from 'firebase/app';
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';

const firebaseConfig = {
  // Your config here
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Test login
signInWithEmailAndPassword(auth, 'test@example.com', 'testpass123')
  .then((userCredential) => {
    console.log('Login successful:', userCredential.user.uid);
  })
  .catch((error) => {
    console.error('Login failed:', error);
  });
```

## Security Best Practices

1. **Never commit credentials to version control**
   - Add `firebase-service-account.json` to `.gitignore`
   - Use environment variables for all sensitive data

2. **Use different Firebase projects for environments**
   - Development: `cmms-dev`
   - Staging: `cmms-staging`
   - Production: `cmms-production`

3. **Restrict API keys**
   - In Firebase Console → Project Settings → API restrictions
   - Restrict to specific domains for web apps

4. **Enable App Check** (optional but recommended)
   - Protects your backend from abuse
   - Go to Firebase Console → Build → App Check

5. **Set up Firebase Security Rules**
   - Firestore: Restrict access to authenticated users
   - Storage: Restrict file uploads/downloads

## Troubleshooting

### "Permission denied" errors
- Verify service account has correct IAM roles
- Check that `FIREBASE_CREDENTIALS_PATH` points to correct file

### "Invalid API key" errors
- Verify all Firebase config values are correct
- Check that API key is not restricted to wrong domains

### "User not found" errors
- Verify user exists in Firebase Authentication console
- Check that `firebase_uid` is correctly stored in Django User model

## Next Steps

After completing this setup:
1. Run Task 2: Create database migration for firebase_uid field
2. Implement backend Firebase authentication components
3. Update frontend to use Firebase Authentication
