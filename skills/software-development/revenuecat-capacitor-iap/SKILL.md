---
name: revenuecat-capacitor-iap
description: Universal RevenueCat + IAP setup for Capacitor apps — covers RevenueCat dashboard, App Store Connect IAP, Google Play subscriptions, service accounts, SDK integration, and webhook sync. Use this for any Capacitor/React app.
triggers:
  - "revenuecat"
  - "in-app purchase"
  - "IAP setup"
  - "subscription setup"
  - "google play billing"
  - "app store iap"
  - "purchases capacitor"
---

# RevenueCat + IAP — Capacitor App Setup Guide

## Overview

RevenueCat is the single source of truth for mobile In-App Purchases on iOS and Android.
Web uses a separate payment system (Stripe, PayPal, etc.). RevenueCat syncs purchase state
back to your backend via webhooks to keep all platforms consistent.

Architecture:
  iOS/Android: RevenueCat SDK (Capacitor) → purchase → RC dashboard → webhook → backend
  Web:         Separate payment SDK → purchase → webhook → backend


## Prerequisites

- Apple Developer account ($99/yr) with App Store Connect access
- Google Play Console access
- Capacitor 6+ project (iOS + Android)
- RevenueCat account (free tier supports up to ~$2.5K tracked revenue)
- Backend with webhook endpoint (Firebase Functions, etc.)


## Step 1 — App Store Connect IAP Products

1. Go to https://appstoreconnect.apple.com → Your App → Monetization → Subscriptions
2. Create a subscription group (e.g. "Pro")
3. For each plan (monthly, annual, etc.):
     - Reference Name:  YOUR_APP Pro Monthly
     - Product ID:      com.yourdomain.app_pro_monthly  (must be unique, lowercase, underscores)
     - Price:           Set price tier (e.g. tier 9 = $9.99/mo)
     - Duration:        1 Month / 1 Year
     - Display name:    Pro
     - Description:     What the subscription includes
4. Submit for review — status: "Ready to Submit" → "Approved" (happens with first binary)

**Important:**
- IAP products cannot be purchased in production until "Approved"
- Sandbox testing works during "Ready to Submit" state for TestFlight
- Apple often reviews IAP products together with the first binary submission


## Step 2 — App Store Connect API Key (for RevenueCat)

RevenueCat needs an ASC API key to communicate with Apple on your behalf.

1. Go to https://appstoreconnect.apple.com → Users & Access → Integrations → App Store Connect API
2. Generate API key:
     Name:    RevenueCat
     Role:    Developer (Admin also works but Developer is least privilege needed)
     Access:  Select your app(s)
3. Download the `.p8` key file — **you only get one download**, store it securely
4. Note the Key ID and Issuer ID from the same page
5. Note your Vendor ID: App Store Connect → Agreements → Tax → Banking → Vendor number

**Values you'll need in RC dashboard:**
- Key ID:      (from ASC API page)
- Issuer ID:   (from ASC API page)
- Vendor ID:   (from Agreements page)
- .p8 key file: (the downloaded file)


## Step 3 — S2S Notifications (Apple → RevenueCat)

Apple pushes renewal/cancellation events to RevenueCat via Server-to-Server notifications.

1. In RevenueCat dashboard → Your iOS app → Configuration
2. RC will provide a notification URL — copy it
3. In App Store Connect → Your App → App Information → App Store Server Notifications V2
4. Set Production URL to the URL RC provided
5. Set Sandbox URL to the same URL (or RC's sandbox-specific URL if provided)

This is critical — without S2S, RevenueCat won't know about automatic renewals or cancellations.


## Step 4 — Google Play Console IAP Products

1. Go to https://play.google.com/console → Your App → Monetize → Subscriptions
2. Create subscription for each plan:
     Product ID:  monthly_base  (alphanumeric, underscores, no dots)
     Name:        Pro Monthly
     Price:       Set price
     Free trial:  Optional (e.g. 7 days)
3. **Activate / Publish** each subscription — draft status is invisible to RevenueCat
4. Note: Play Store requires at least one release (even internal testing) before subscriptions can be activated


## Step 5 — Google Play Service Account

RevenueCat needs a service account with financial data access to validate Android purchases.

**Create the service account:**
1. Google Play Console → Setup → API access
2. Link your Google Cloud project (or create one)
3. Create service account in Google Cloud Console → IAM → Service Accounts
4. Download JSON key — store securely

**Grant Play Console permissions** (NOT Google Cloud IAM — these are separate!):
1. Google Play Console → Setup → API access → View linked service accounts
2. Click the service account → grant permissions:
     - View app information and download bulk reports
     - View financial data, orders, and cancellation survey responses
     - Manage orders and subscriptions
3. Save

**CRITICAL:** IAM roles in Google Cloud do NOT grant Play Console access.
Permissions must be granted in the Play Console UI directly. This is the #1 Android IAP pitfall.


## Step 6 — RevenueCat Dashboard Setup

### Create apps
1. RC Project → Apps → New app → iOS → enter bundle ID, upload .p8 key, fill Key ID, Issuer ID, Vendor ID
2. RC Project → Apps → New app → Android → enter package name, paste service account JSON

### Create entitlement
RC Project → Product catalog → Entitlements → Create
  Identifier:  YOUR_ENTITLEMENT_NAME  (e.g. "Pro")
  Description: What this entitlement grants

Attach all products (iOS + Android) to this entitlement.

### Create products
RC Project → Product catalog → Products → Add
  Add each product ID from App Store Connect and Google Play.
  RC auto-fetches price/description once the app configs are linked.

### Create offering
RC Project → Product catalog → Offerings → Create
  Identifier:  default
  Packages:
    $rc_monthly → attach iOS monthly + Android monthly
    $rc_annual  → attach iOS annual + Android annual

The "default" offering is what `getCurrentOffering()` returns in code.
Packages need at least one product attached before they appear in the app.


## Step 7 — Webhook (RevenueCat → Your Backend)

RevenueCat posts purchase events to your backend to keep your database in sync.

Configure in RC dashboard → Integrations → Webhooks → Add:
  URL:    YOUR_WEBHOOK_URL (e.g. Firebase Function endpoint)
  Events: INITIAL_PURCHASE, RENEWAL, CANCELLATION, EXPIRATION, BILLING_ISSUE, PRODUCT_CHANGE

Your webhook should:
  1. Verify the event is legitimate (RC signs webhook payloads)
  2. Extract `app_user_id` → this is your user ID (e.g. Firebase UID)
  3. Write subscription status to your database (e.g. Firestore users/{uid}.subscription)
  4. Return 200 OK

**Important:** The `app_user_id` in RC must match your backend user ID.
Set this via `Purchases.logIn({ appUserID: yourUserId })` when the user authenticates.


## Step 8 — SDK Installation

```bash
npm install @revenuecat/purchases-capacitor @revenuecat/purchases-capacitor-ui
npx cap sync ios
npx cap sync android
```


## Step 9 — SDK Keys (Environment Variables)

Keys come from RC dashboard → Your app → API keys → Secret API key

Set in your hosting platform (Vercel, etc.):
  VITE_REVENUECAT_API_KEY_IOS      = appl_xxxxxxx
  VITE_REVENUECAT_API_KEY_ANDROID  = goog_xxxxxxx

CRITICAL — prevent trailing newline corruption when setting env vars:
  printf '%s' 'appl_xxxxxxx' | npx vercel env add VITE_REVENUECAT_API_KEY_IOS production
NEVER use `echo` — it appends \n which silently corrupts the value.
A corrupted key is truthy (passes `??` null check) but RC SDK rejects it,
falling back to the test key and crashing on non-debug/TestFlight builds.

Symptom: "This app is using a test API key" crash dialog on TestFlight.
Verify: check stored value via hosting API — should not end with \n.

Test key (dev only): `test_otBoYqbuWFiQXFMeeQksIMmkrzY`


## Step 10 — Code Integration

### Service wrapper (src/services/revenuecat.ts)

```ts
import { Capacitor } from '@capacitor/core';
import {
  Purchases, LOG_LEVEL, PURCHASES_ERROR_CODE,
  type CustomerInfo, type PurchasesOffering, type PurchasesPackage,
} from '@revenuecat/purchases-capacitor';
import {
  RevenueCatUI, type PaywallListener, PAYWALL_RESULT,
} from '@revenuecat/purchases-capacitor-ui';

const platform = Capacitor.getPlatform();
const API_KEY: string =
  (platform === 'ios' ? import.meta.env.VITE_REVENUECAT_API_KEY_IOS
   : platform === 'android' ? import.meta.env.VITE_REVENUECAT_API_KEY_ANDROID
   : undefined)
  ?? import.meta.env.VITE_REVENUECAT_API_KEY
  ?? 'test_otBoYqbuWFiQXFMeeQksIMmkrzY';

export const ENTITLEMENT_PRO = 'YOUR_ENTITLEMENT_NAME';  // must match RC dashboard
export const OFFERING_DEFAULT = 'default';

let _initialized = false;

export async function initRevenueCat(
  userId?: string,
  onCustomerInfoUpdated?: (info: CustomerInfo) => void,
): Promise<void> {
  if (!Capacitor.isNativePlatform() || _initialized) return;
  await Purchases.setLogLevel({ level: LOG_LEVEL.DEBUG });
  await Purchases.configure({
    apiKey: API_KEY,
    ...(userId ? { appUserID: userId } : {}),
  });
  _initialized = true;
  if (onCustomerInfoUpdated) {
    await Purchases.addCustomerInfoUpdateListener(onCustomerInfoUpdated);
  }
}

export async function identifyRevenueCatUser(userId: string): Promise<CustomerInfo | null> {
  if (!Capacitor.isNativePlatform()) return null;
  try {
    const { customerInfo } = await Purchases.logIn({ appUserID: userId });
    return customerInfo;
  } catch { return null; }
}

export async function logOutRevenueCat(): Promise<void> {
  if (!Capacitor.isNativePlatform()) return;
  try { await Purchases.logOut(); } catch {}
}

export function isCustomerInfoPro(info: CustomerInfo): boolean {
  return info.entitlements.active[ENTITLEMENT_PRO] !== undefined;
}

export async function hasProEntitlement(): Promise<boolean> {
  const info = await (await import('@revenuecat/purchases-capacitor')).Purchases.getCustomerInfo()
    .then(r => r.customerInfo).catch(() => null);
  return info ? isCustomerInfoPro(info) : false;
}

export async function presentPaywallIfNeeded(
  offering?: PurchasesOffering,
  listener?: PaywallListener,
) {
  if (!Capacitor.isNativePlatform()) return { purchased: false, dismissed: true, restored: false };
  try {
    const { result } = await RevenueCatUI.presentPaywallIfNeeded({
      requiredEntitlementIdentifier: ENTITLEMENT_PRO,
      ...(offering ? { offering } : {}),
      displayCloseButton: true,
      listener,
    });
    return {
      purchased: result === PAYWALL_RESULT.PURCHASED,
      dismissed: result === PAYWALL_RESULT.NOT_PRESENTED || result === PAYWALL_RESULT.CANCELLED,
      restored: result === PAYWALL_RESULT.RESTORED,
    };
  } catch (err) {
    return { purchased: false, dismissed: false, restored: false, error: String(err) };
  }
}

export async function restorePurchases() {
  if (!Capacitor.isNativePlatform()) return { success: false, isPro: false };
  const { customerInfo } = await Purchases.restorePurchases();
  return { success: true, isPro: isCustomerInfoPro(customerInfo) };
}

export async function presentCustomerCenter() {
  if (!Capacitor.isNativePlatform()) return;
  await RevenueCatUI.presentCustomerCenter().catch(() => {});
}
```

### React context (src/contexts/SubscriptionContext.tsx)

```tsx
// Wraps the app. On native: RC SDK is source of truth (real-time listener).
// On web: your backend is source of truth (e.g. Firestore subscription doc).
// Belt-and-braces: isPro = backendIsPro || rcPro
//
// Key pattern: call initRevenueCat(uid, callback) then identifyRevenueCatUser(uid)
// on every user login. Call logOutRevenueCat() on sign-out.
// Use addCustomerInfoUpdateListener for real-time renewal/cancellation updates.
```

### Route setup
```tsx
// /pricing route:
//   native → NativePaywall (RevenueCat)
//   web    → PricingPage (Stripe/PayPal/whatever)
```

### App Store requirement
Your paywall MUST include a "Restore Purchases" button. Apple will reject without it.


## Encryption Export Compliance

When App Store Connect asks about encryption, select:
**"None of the algorithms mentioned above"**

Your app uses HTTPS/TLS which is Apple's OS-level encryption — this does NOT count
as custom encryption implementation. Unless you are using custom crypto libraries
(CryptoKit, CommonCrypto directly), select "None".


## Common Issues & Fixes

**"Wrong API Key" crash on TestFlight**
Cause: SDK key has trailing \n from env var corruption.
Fix: re-set using `printf '%s'` (see Step 9). Rebuild + resubmit.

**Offering returns null / no packages**
Cause: Products not attached to packages in RC, or store products not active.
Fix: Play products must be "Published". iOS must be at least "Ready to Submit".
RC caches offerings — allow ~5 min after changes.

**"Invalid purchase" on Android**
Cause: App not in any testing track, or service account lacks Play Console permissions.
Fix: Upload to Internal Testing. Grant permissions in Play Console (NOT GCP IAM).

**iOS sandbox works but production fails**
Cause: IAP products not "Approved" yet.
Fix: Submit binary + IAP together for review.

**RC not syncing to backend**
Cause: Webhook not receiving events, or user IDs don't match.
Fix: Check RC → Integrations → Webhooks → Logs. Ensure Purchases.logIn(uid) is called.

**"Service account has insufficient permissions"**
Cause: Permissions granted in GCP IAM instead of Play Console.
Fix: Grant in Play Console → Users & Permissions directly.

**"No app found with bundle ID"**
Cause: Bundle ID mismatch between RC config, Xcode, and App Store Connect.
Fix: Must match exactly across all three.

**Test key works but production key doesn't**
Cause: Production key corrupted with trailing \n, or wrong key for platform.
Fix: Verify via hosting API (repr check). Ensure iOS key on iOS, Android key on Android.


## Checklist — Full Setup From Scratch

**App Store Connect:**
  [ ] Create subscription group
  [ ] Add subscription products (monthly, annual, etc.)
  [ ] Submit for review (with first binary)
  [ ] Note Vendor ID (Agreements → Tax → Banking)
  [ ] Generate ASC API key (.p8) with Developer role
  [ ] Set S2S notification URL → RC-provided URL

**Google Play Console:**
  [ ] Create subscription products
  [ ] Activate / Publish all subscriptions
  [ ] Create service account in GCP
  [ ] Grant Play Console financial permissions (NOT IAM)
  [ ] Download JSON key

**RevenueCat Dashboard:**
  [ ] Create iOS app (bundle ID, ASC key, vendor ID)
  [ ] Create Android app (package name, service account JSON)
  [ ] Add all products to catalog
  [ ] Create entitlement → attach all products
  [ ] Create "default" offering → add packages
  [ ] Configure webhook → backend URL
  [ ] Copy SDK keys → set in hosting env vars (use printf '%s'!)

**Code:**
  [ ] Install @revenuecat/purchases-capacitor + ui
  [ ] Create revenuecat.ts service wrapper
  [ ] Create SubscriptionContext with init + identify + logout
  [ ] Call initRevenueCat(uid) + identifyRevenueCatUser(uid) on login
  [ ] Call logOutRevenueCat() on sign-out
  [ ] Route /pricing → NativePaywall (native) / PricingPage (web)
  [ ] Add "Restore Purchases" button to paywall
  [ ] Verify entitlement ID matches RC dashboard exactly
