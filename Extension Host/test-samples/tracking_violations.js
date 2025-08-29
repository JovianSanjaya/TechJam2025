// Sample JavaScript code with compliance violations
// This file demonstrates various privacy and regulatory violations

class SocialMediaTracker {
    constructor() {
        this.userProfiles = new Map();
        this.behaviorLog = [];
        this.locationHistory = new Map();
    }

    // VIOLATION: Collecting personal data without explicit consent
    collectUserProfile(userId, profileData) {
        const userProfile = {
            id: userId,
            name: profileData.name,
            email: profileData.email,
            phone: profileData.phone,
            age: profileData.age,
            location: profileData.location,
            interests: profileData.interests,
            socialConnections: profileData.friends,
            deviceInfo: this.getDeviceFingerprint(),
            ipAddress: this.getClientIP(),
            browserHistory: this.getBrowserHistory()
        };

        // VIOLATION: Storing sensitive data without encryption
        this.userProfiles.set(userId, userProfile);

        // VIOLATION: Sharing data with third parties without consent
        this.shareWithAdvertisingPartners(userProfile);

        return userProfile;
    }

    // VIOLATION: Device fingerprinting without consent
    getDeviceFingerprint() {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        ctx.textBaseline = 'top';
        ctx.font = '14px Arial';
        ctx.fillText('fingerprint', 2, 2);

        return {
            canvasFingerprint: canvas.toDataURL(),
            screenResolution: `${screen.width}x${screen.height}`,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            language: navigator.language,
            platform: navigator.platform,
            cookieEnabled: navigator.cookieEnabled,
            plugins: Array.from(navigator.plugins).map(p => p.name)
        };
    }

    // VIOLATION: Tracking IP address without consent
    getClientIP() {
        // This would typically involve server-side tracking
        return '192.168.1.100'; // Mock IP
    }

    // VIOLATION: Accessing browser history without permission
    getBrowserHistory() {
        // This is a violation - accessing browser history
        if (window.performance && window.performance.getEntriesByType) {
            return window.performance.getEntriesByType('navigation');
        }
        return [];
    }

    // VIOLATION: Location tracking without proper consent
    trackUserLocation(userId) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const locationData = {
                        userId: userId,
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: new Date().toISOString(),
                        altitude: position.coords.altitude,
                        heading: position.coords.heading,
                        speed: position.coords.speed
                    };

                    // VIOLATION: Storing location history indefinitely
                    if (!this.locationHistory.has(userId)) {
                        this.locationHistory.set(userId, []);
                    }
                    this.locationHistory.get(userId).push(locationData);

                    // VIOLATION: Sharing location with third parties
                    this.shareLocationWithPartners(userId, locationData);
                },
                (error) => {
                    console.error('Location tracking failed:', error);
                }
            );
        }
    }

    // VIOLATION: Sharing location data with advertising partners
    shareLocationWithPartners(userId, locationData) {
        const partners = [
            'facebook.com',
            'google-analytics.com',
            'tiktok.com',
            'advertising-network.com'
        ];

        partners.forEach(partner => {
            fetch(`https://${partner}/track-location`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    userId: userId,
                    location: locationData,
                    consent: false // VIOLATION: No consent obtained
                })
            });
        });
    }

    // VIOLATION: Behavioral tracking without consent
    trackUserBehavior(userId, action, element) {
        const behaviorData = {
            userId: userId,
            action: action,
            element: element,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent,
            sessionId: this.getSessionId(),
            referrer: document.referrer
        };

        this.behaviorLog.push(behaviorData);

        // VIOLATION: Real-time behavioral analysis
        this.analyzeBehaviorForAdvertising(userId, behaviorData);
    }

    // VIOLATION: Analyzing behavior for targeted advertising
    analyzeBehaviorForAdvertising(userId, behaviorData) {
        const interests = this.extractInterests(behaviorData);
        const profile = this.userProfiles.get(userId);

        if (profile) {
            profile.interests = [...new Set([...profile.interests, ...interests])];
            this.userProfiles.set(userId, profile);
        }

        // VIOLATION: Creating advertising profiles
        this.updateAdvertisingProfile(userId, interests);
    }

    extractInterests(behaviorData) {
        const interests = [];
        const url = behaviorData.url.toLowerCase();

        if (url.includes('sports')) interests.push('sports');
        if (url.includes('music')) interests.push('music');
        if (url.includes('gaming')) interests.push('gaming');
        if (url.includes('shopping')) interests.push('shopping');
        if (url.includes('travel')) interests.push('travel');

        return interests;
    }

    // VIOLATION: Age verification bypass
    processUserRegistration(userData) {
        // VIOLATION: No proper age verification
        if (userData.age < 13) {
            // VIOLATION: Collecting additional data on children
            this.collectChildData(userData);
        } else if (userData.age < 16) {
            // VIOLATION: Applying insufficient privacy restrictions
            this.applyMinimalRestrictions(userData);
        } else {
            // VIOLATION: No consent for adult users either
            this.processAdultData(userData);
        }
    }

    // VIOLATION: Collecting children's data without parental consent
    collectChildData(childData) {
        const childProfile = {
            ...childData,
            school: this.getSchoolInfo(childData.id),
            parents: this.getParentInfo(childData.id),
            friends: this.getFriendsList(childData.id),
            onlineActivity: this.getActivityLog(childData.id),
            interests: this.getChildInterests(childData.id)
        };

        // VIOLATION: Storing children's data
        this.userProfiles.set(childData.id, childProfile);
    }

    // VIOLATION: Processing data without proper consent mechanisms
    exportUserData(userId) {
        const userData = this.userProfiles.get(userId);
        if (!userData) return null;

        // VIOLATION: Exporting sensitive data without user knowledge
        const exportData = {
            ...userData,
            internalNotes: this.getInternalNotes(userId),
            riskScore: this.calculateRiskScore(userId),
            marketingValue: this.calculateMarketingValue(userId),
            behaviorPatterns: this.analyzeBehaviorPatterns(userId)
        };

        return JSON.stringify(exportData, null, 2);
    }

    // VIOLATION: Creating comprehensive user profiles
    createUserProfile(userId) {
        const profile = this.userProfiles.get(userId);
        const behavior = this.behaviorLog.filter(log => log.userId === userId);
        const locations = this.locationHistory.get(userId) || [];

        return {
            basicInfo: profile,
            behaviorHistory: behavior,
            locationHistory: locations,
            interests: this.extractInterestsFromHistory(behavior),
            socialGraph: this.buildSocialGraph(userId),
            riskProfile: this.assessRiskProfile(userId)
        };
    }
}

// Usage example with violations
const tracker = new SocialMediaTracker();

// VIOLATION: Processing user data without consent
const testUsers = [
    { id: 1, name: 'Child User', age: 12 },
    { id: 2, name: 'Teen User', age: 15 },
    { id: 3, name: 'Adult User', age: 25 }
];

testUsers.forEach(user => {
    tracker.collectUserProfile(user.id, user);
    tracker.trackUserLocation(user.id);
    tracker.trackUserBehavior(user.id, 'click', 'like-button');
    tracker.processUserRegistration(user);
});

console.log('Tracking initialized for all users');
