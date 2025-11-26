# Implementation Plan

- [x] 1. Setup Firebase project and configuration



  - Create Firebase project in Google Cloud Console
  - Enable Firebase Authentication service
  - Download service account credentials JSON file
  - Add Firebase configuration to backend .env files
  - Add Firebase configuration to frontend .env files
  - Install firebase-admin package in backend requirements.txt
  - Install firebase package in frontend package.json




  - _Requirements: 1.1, 2.1_

- [-] 2. Create database migration for firebase_uid field



  - Create Django migration to add firebase_uid field to User model
  - Add unique constraint and index on firebase_uid



  - Test migration in development environment
  - Test migration rollback
  - _Requirements: 3.2_

- [ ] 3. Implement backend Firebase authentication components
- [ ] 3.1 Create FirebaseAuthentication DRF class
  - Implement authenticate() method to validate Firebase ID tokens
  - Implement get_token_from_header() to extract Bearer token
  - Implement verify_firebase_token() using Firebase Admin SDK
  - Implement get_or_create_user() to load Django user by firebase_uid
  - Implement token validation caching with 5-minute TTL
  - Handle authentication errors (invalid token, expired token, user not found)
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_



- [ ] 3.2 Write property test for token validation
  - **Property 6: Token validation correctness**
  - **Validates: Requirements 2.1, 2.3**

- [ ] 3.3 Write property test for user attachment
  - **Property 7: Valid token attaches correct user**
  - **Validates: Requirements 2.2**

- [ ] 3.4 Write property test for token caching
  - **Property 8: Token validation caching**
  - **Validates: Requirements 2.4**

- [ ] 3.5 Create FirebaseUserService
  - Implement create_firebase_user() to create Firebase accounts
  - Implement update_firebase_user() to update email/password/display_name
  - Implement disable_firebase_user() and enable_firebase_user()
  - Implement delete_firebase_user()
  - Implement send_password_reset_email()
  - Add error handling and retry logic with exponential backoff


  - _Requirements: 3.1, 3.3, 3.4, 3.5, 7.1, 7.2, 7.3, 9.1, 9.2_

- [ ] 3.6 Write property test for user creation sync
  - **Property 9: User creation creates Firebase account and stores UID**
  - **Validates: Requirements 3.1, 3.2**

- [ ] 3.7 Write property test for password sync
  - **Property 10: Password changes sync to Firebase**
  - **Validates: Requirements 3.3**

- [ ] 3.8 Write property test for user deactivation sync
  - **Property 11: User deactivation syncs to Firebase**
  - **Validates: Requirements 3.4, 3.5, 7.3**

- [ ] 3.9 Create CustomClaimsService
  - Implement build_claims_for_user() to create claims dictionary
  - Include role, role_display, permissions, role flags, employee_status
  - Implement _get_license_status() for operador users
  - Implement update_user_claims() to set claims in Firebase
  - _Requirements: 4.1, 4.2, 4.4, 6.1_

- [-] 3.10 Write property test for custom claims structure



  - **Property 12: Custom claims contain complete user data**
  - **Validates: Requirements 4.1, 4.2**

- [ ] 3.11 Write property test for role changes updating claims
  - **Property 14: Role changes update custom claims**
  - **Validates: Requirements 4.4, 4.5**

- [ ] 3.12 Write property test for license status in claims
  - **Property 18: License status in custom claims**
  - **Validates: Requirements 6.1**

- [ ] 3.13 Write property test for license validation
  - **Property 19: License validation correctness**
  - **Validates: Requirements 6.2, 6.3, 6.4**




- [ ] 4. Implement user synchronization with Django signals
- [ ] 4.1 Create signals.py for authentication app
  - Implement post_save signal to sync user changes to Firebase
  - Implement pre_delete signal to delete Firebase user on Django user deletion
  - Handle user creation (create Firebase account and store UID)
  - Handle user updates (update Firebase email, password, display_name)
  - Handle user activation/deactivation (enable/disable Firebase account)
  - Update custom claims when role or permissions change
  - Add transaction handling to rollback on Firebase failures
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 7.1, 7.5_

- [ ] 4.2 Write property test for admin user creation
  - **Property 20: Admin user creation creates Firebase account**
  - **Validates: Requirements 7.1, 7.5**

- [ ] 4.3 Write property test for admin password reset
  - **Property 21: Admin password reset syncs to Firebase**
  - **Validates: Requirements 7.2**

- [ ] 4.4 Implement error logging for Firebase operations
  - Create logger for Firebase operations
  - Log all Firebase API calls with operation type, user ID, and result
  - Log errors with full stack traces and context
  - Add correlation IDs to all log entries
  - _Requirements: 7.4, 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 4.5 Write property test for Firebase operation logging
  - **Property 22: Firebase operation failures are logged**
  - **Validates: Requirements 7.4**

- [ ] 4.6 Write property test for authentication logging
  - **Property 26: Successful authentication is logged**
  - **Property 27: Failed authentication is logged**
  - **Validates: Requirements 10.1, 10.2**

- [ ] 4.7 Write property test for correlation IDs
  - **Property 29: Logs include correlation IDs**
  - **Validates: Requirements 10.5**

- [ ] 5. Update Django settings and configuration
- [ ] 5.1 Update REST_FRAMEWORK settings
  - Replace JWTAuthentication with FirebaseAuthentication in DEFAULT_AUTHENTICATION_CLASSES
  - Keep existing permission classes unchanged
  - Update SIMPLE_JWT settings to mark as deprecated
  - _Requirements: 5.1, 5.2, 5.3_




- [ ] 5.2 Add Firebase configuration settings
  - Add FIREBASE_CREDENTIALS_PATH setting
  - Add FIREBASE_DATABASE_URL setting
  - Add FIREBASE_STORAGE_BUCKET setting

  - Add FIREBASE_TOKEN_CACHE_TTL setting (default 300 seconds)
  - Add environment variables to .env.example
  - _Requirements: 2.1, 2.4_

- [ ] 5.3 Update authentication URLs
  - Keep existing endpoints for backward compatibility
  - Add new Firebase-specific endpoints if needed
  - Update API documentation
  - _Requirements: 1.1, 9.1_


- [ ] 5.4 Write property test for backward compatibility
  - **Property 15: Existing user model methods work**
  - **Property 16: Existing permission classes work**
  - **Property 17: User data integrity**
  - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**



- [ ] 6. Implement frontend Firebase integration
- [ ] 6.1 Create Firebase configuration file
  - Create frontend/src/config/firebase.ts
  - Initialize Firebase app with environment variables
  - Export auth instance
  - Add Firebase config to .env.example
  - _Requirements: 1.1_

- [x] 6.2 Update AuthService for Firebase

  - Replace JWT login with signInWithEmailAndPassword
  - Implement logout with signOut
  - Implement getIdToken() to get current token
  - Implement onAuthStateChanged listener
  - Remove old JWT token management code
  - Store Firebase token in localStorage
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 6.3 Write property test for frontend login
  - **Property 1: Successful login returns valid Firebase token**
  - **Validates: Requirements 1.1**

- [ ] 6.4 Write property test for token storage
  - **Property 2: Token storage and usage**
  - **Validates: Requirements 1.2**

- [-] 6.5 Write property test for token refresh



  - **Property 3: Automatic token refresh**
  - **Validates: Requirements 1.3**

- [ ] 6.6 Write property test for logout
  - **Property 4: Logout clears all authentication state**
  - **Validates: Requirements 1.4**

- [ ] 6.7 Write property test for error handling
  - **Property 5: Authentication errors display appropriate messages**
  - **Validates: Requirements 1.5**

- [ ] 6.8 Update API client interceptors
  - Update request interceptor to get Firebase token from auth.currentUser
  - Update response interceptor to handle 401 with token refresh
  - Remove old JWT refresh logic
  - Add error handling for Firebase token errors
  - _Requirements: 1.2, 1.3_

- [ ] 6.9 Update authentication context/hooks
  - Update useAuth hook to use Firebase onAuthStateChanged


  - Update user state management to use Firebase user
  - Decode custom claims from Firebase token
  - Expose permissions from custom claims
  - _Requirements: 4.3_

- [ ] 6.10 Write property test for custom claims decoding
  - **Property 13: Frontend can decode custom claims**
  - **Validates: Requirements 4.3**

- [ ] 7. Create user migration script
- [ ] 7.1 Implement migration script
  - Create management command: migrate_users_to_firebase
  - Query all users without firebase_uid
  - For each user, create Firebase account with temporary password
  - Store Firebase UID in user.firebase_uid
  - Set custom claims for each user
  - Log successful and failed migrations
  - Generate report of migration results
  - _Requirements: 8.1, 8.2, 8.4, 8.5_

- [ ] 7.2 Write property test for migration
  - **Property 23: Migration creates Firebase accounts for all users**
  - **Validates: Requirements 8.1, 8.2**

- [ ] 7.3 Write property test for existing account handling
  - **Property 24: Migration handles existing Firebase accounts**
  - **Validates: Requirements 8.4**

- [ ] 7.4 Write property test for migration error resilience
  - **Property 25: Migration error resilience**
  - **Validates: Requirements 8.5**

- [ ] 7.5 Create password reset email script
  - Create management command: send_migration_emails
  - Query all migrated users
  - Send password reset email to each user via Firebase
  - Include instructions for first-time login
  - Log email sending results
  - _Requirements: 8.3, 9.1, 9.2_

- [ ] 8. Update documentation
  - Update API documentation with Firebase authentication flow
  - Document environment variables for Firebase configuration
  - Create migration guide for administrators
  - Update user guide with new login process
  - Document rollback procedure
  - _Requirements: All_

- [ ] 9. Checkpoint - Ensure all tests pass
  - Run all unit tests
  - Run all property-based tests
  - Run integration tests
  - Verify test coverage meets requirements
  - Fix any failing tests
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Deploy to staging environment
- [ ] 10.1 Deploy backend changes
  - Deploy updated backend code to staging
  - Run database migrations
  - Verify Firebase credentials are configured
  - Test authentication endpoints
  - Monitor logs for errors
  - _Requirements: All_

- [ ] 10.2 Deploy frontend changes
  - Deploy updated frontend code to staging
  - Verify Firebase configuration
  - Test login/logout flows
  - Test token refresh
  - Monitor browser console for errors
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 10.3 Run migration script in staging
  - Backup staging database
  - Run migrate_users_to_firebase command
  - Verify all users have firebase_uid
  - Test login with migrated users
  - Send test password reset emails
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 10.4 Perform end-to-end testing in staging
  - Test complete login flow
  - Test token refresh
  - Test logout
  - Test password reset
  - Test user creation by admin
  - Test role changes and custom claims updates
  - Test license validation for operador users
  - Verify all existing functionality still works
  - _Requirements: All_

- [ ] 11. Deploy to production
- [ ] 11.1 Prepare production deployment
  - Create deployment checklist
  - Schedule maintenance window
  - Notify users of upcoming changes
  - Backup production database
  - Prepare rollback plan
  - _Requirements: All_

- [ ] 11.2 Deploy backend to production
  - Deploy updated backend code
  - Run database migrations
  - Verify Firebase credentials
  - Monitor logs for errors
  - Test authentication endpoints
  - _Requirements: All_

- [ ] 11.3 Run production migration
  - Run migrate_users_to_firebase command
  - Monitor migration progress
  - Verify all users migrated successfully
  - Review migration report
  - _Requirements: 8.1, 8.2, 8.4, 8.5_

- [ ] 11.4 Send password reset emails to users
  - Run send_migration_emails command
  - Monitor email sending progress
  - Verify emails are delivered
  - Prepare support for user questions
  - _Requirements: 8.3, 9.1, 9.2_

- [ ] 11.5 Deploy frontend to production
  - Deploy updated frontend code
  - Verify Firebase configuration
  - Monitor authentication success rate
  - Check for client-side errors
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 11.6 Monitor production deployment
  - Monitor authentication success/failure rates
  - Monitor Firebase API usage and quota
  - Monitor application logs for errors
  - Monitor user feedback and support requests
  - Track migration completion rate
  - _Requirements: All_

- [ ] 12. Final checkpoint - Verify production deployment
  - Verify all users can authenticate
  - Verify all existing functionality works
  - Verify custom claims are set correctly
  - Verify license validation works for operadores
  - Verify audit logs are being created
  - Ensure all tests pass, ask the user if questions arise.
