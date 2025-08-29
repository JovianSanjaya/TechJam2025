// Sample TypeScript code with compliance violations
// This file demonstrates various privacy and regulatory violations in TypeScript

interface UserProfile {
    id: number;
    name: string;
    email: string;
    age: number;
    location?: LocationData;
    interests: string[];
    socialConnections: number[];
}

interface LocationData {
    latitude: number;
    longitude: number;
    accuracy: number;
    timestamp: string;
}

interface BehaviorLog {
    userId: number;
    action: string;
    timestamp: string;
    metadata: any;
}

class DataCollectionService {
    private userDatabase: Map<number, UserProfile> = new Map();
    private behaviorLogs: BehaviorLog[] = [];
    private locationHistory: Map<number, LocationData[]> = new Map();

    // VIOLATION: Collecting personal data without explicit consent
    public collectUserData(userId: number, rawData: any): UserProfile {
        const userProfile: UserProfile = {
            id: userId,
            name: rawData.name,
            email: rawData.email,
            age: rawData.age,
            interests: rawData.interests || [],
            socialConnections: rawData.friends || [],
            location: this.getCurrentLocation(userId)
        };

        // VIOLATION: Storing sensitive data without encryption
        this.userDatabase.set(userId, userProfile);

        // VIOLATION: Sharing data with third parties without consent
        this.shareWithPartners(userProfile);

        return userProfile;
    }

    // VIOLATION: Location tracking without proper consent
    private getCurrentLocation(userId: number): LocationData | undefined {
        if (navigator.geolocation) {
            // VIOLATION: Getting location without user permission
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const locationData: LocationData = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: new Date().toISOString()
                    };

                    // VIOLATION: Storing location history indefinitely
                    this.storeLocationData(userId, locationData);

                    // VIOLATION: Sharing location with advertising networks
                    this.shareLocationWithAdvertisers(userId, locationData);
                },
                (error) => console.error('Location error:', error)
            );
        }
        return undefined;
    }

    // VIOLATION: Storing location data without retention policy
    private storeLocationData(userId: number, location: LocationData): void {
        if (!this.locationHistory.has(userId)) {
            this.locationHistory.set(userId, []);
        }
        this.locationHistory.get(userId)!.push(location);
    }

    // VIOLATION: Sharing location data with third parties
    private shareLocationWithAdvertisers(userId: number, location: LocationData): void {
        const advertisingPartners = [
            'facebook.com',
            'google-analytics.com',
            'tiktok-marketing.com',
            'ad-network.com'
        ];

        advertisingPartners.forEach(partner => {
            fetch(`https://${partner}/location-track`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    userId: userId,
                    location: location,
                    consentObtained: false // VIOLATION: No consent
                })
            });
        });
    }

    // VIOLATION: Sharing user data with partners without consent
    private shareWithPartners(userProfile: UserProfile): void {
        const partners = [
            { name: 'analytics', url: 'analytics.example.com' },
            { name: 'advertising', url: 'ads.example.com' },
            { name: 'social', url: 'social.example.com' }
        ];

        partners.forEach(partner => {
            this.sendDataToPartner(partner.url, userProfile);
        });
    }

    private sendDataToPartner(url: string, data: any): void {
        fetch(`https://${url}/collect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    }

    // VIOLATION: Behavioral tracking without consent
    public trackUserAction(userId: number, action: string, metadata: any = {}): void {
        const logEntry: BehaviorLog = {
            userId: userId,
            action: action,
            timestamp: new Date().toISOString(),
            metadata: {
                ...metadata,
                userAgent: navigator.userAgent,
                url: window.location.href,
                sessionId: this.getSessionId(),
                referrer: document.referrer
            }
        };

        this.behaviorLogs.push(logEntry);

        // VIOLATION: Real-time behavior analysis for profiling
        this.analyzeBehaviorForProfiling(userId, logEntry);
    }

    // VIOLATION: Creating user profiles for advertising
    private analyzeBehaviorForProfiling(userId: number, logEntry: BehaviorLog): void {
        const userProfile = this.userDatabase.get(userId);
        if (!userProfile) return;

        // VIOLATION: Updating interests based on behavior without consent
        const newInterests = this.extractInterestsFromAction(logEntry.action);
        userProfile.interests = [...new Set([...userProfile.interests, ...newInterests])];

        this.userDatabase.set(userId, userProfile);

        // VIOLATION: Creating advertising segments
        this.updateAdvertisingSegments(userId, newInterests);
    }

    private extractInterestsFromAction(action: string): string[] {
        const interestMap: { [key: string]: string[] } = {
            'like_video': ['entertainment', 'video_content'],
            'search_product': ['shopping', 'ecommerce'],
            'visit_sports': ['sports', 'athletics'],
            'music_stream': ['music', 'entertainment'],
            'game_play': ['gaming', 'entertainment']
        };

        return interestMap[action] || [];
    }

    // VIOLATION: Age verification and COPPA compliance issues
    public processUserRegistration(userData: any): void {
        if (userData.age < 13) {
            // VIOLATION: Collecting children's data without parental consent
            this.processChildRegistration(userData);
        } else if (userData.age < 16) {
            // VIOLATION: Insufficient privacy protections for teens
            this.processTeenRegistration(userData);
        } else {
            // VIOLATION: No consent mechanism for adults either
            this.processAdultRegistration(userData);
        }
    }

    // VIOLATION: Processing children's data without COPPA compliance
    private processChildRegistration(childData: any): void {
        const childProfile = {
            ...childData,
            schoolInfo: this.getSchoolInformation(childData.id),
            parentInfo: this.getParentInformation(childData.id),
            friendsList: this.getFriendsList(childData.id),
            activityLog: this.getActivityLog(childData.id),
            interests: this.getChildInterests(childData.id)
        };

        // VIOLATION: Storing comprehensive children's profiles
        this.userDatabase.set(childData.id, childProfile as UserProfile);
    }

    // VIOLATION: Device fingerprinting
    public getDeviceFingerprint(): string {
        const fingerprintData = [
            navigator.userAgent,
            navigator.language,
            screen.width + 'x' + screen.height,
            new Date().getTimezoneOffset(),
            navigator.platform
        ].join('|');

        // VIOLATION: Creating unique identifiers without consent
        return btoa(fingerprintData);
    }

    // VIOLATION: Exporting user data without user knowledge
    public exportUserData(userId: number): string | null {
        const userProfile = this.userDatabase.get(userId);
        if (!userProfile) return null;

        const exportData = {
            ...userProfile,
            behaviorHistory: this.behaviorLogs.filter(log => log.userId === userId),
            locationHistory: this.locationHistory.get(userId) || [],
            internalNotes: this.getInternalNotes(userId),
            riskAssessment: this.assessUserRisk(userId),
            marketingProfile: this.createMarketingProfile(userId)
        };

        return JSON.stringify(exportData, null, 2);
    }

    // VIOLATION: Creating comprehensive marketing profiles
    private createMarketingProfile(userId: number): any {
        const userProfile = this.userDatabase.get(userId);
        const behaviors = this.behaviorLogs.filter(log => log.userId === userId);
        const locations = this.locationHistory.get(userId) || [];

        return {
            demographicSegment: this.calculateDemographicSegment(userProfile!),
            interestClusters: this.clusterUserInterests(userProfile!.interests),
            behavioralPatterns: this.analyzeBehavioralPatterns(behaviors),
            locationPatterns: this.analyzeLocationPatterns(locations),
            marketingValue: this.calculateMarketingValue(userId)
        };
    }

    // Helper methods (simplified for demo)
    private getSessionId(): string {
        return Math.random().toString(36).substring(2);
    }

    private updateAdvertisingSegments(userId: number, interests: string[]): void {
        // Implementation would update advertising segments
    }

    private processTeenRegistration(teenData: any): void {
        // Minimal restrictions - VIOLATION
    }

    private processAdultRegistration(adultData: any): void {
        // No consent - VIOLATION
    }

    private getSchoolInformation(userId: number): any {
        return { school: 'Example School' };
    }

    private getParentInformation(userId: number): any {
        return { parent: 'Example Parent' };
    }

    private getFriendsList(userId: number): number[] {
        return [1, 2, 3];
    }

    private getActivityLog(userId: number): any[] {
        return [];
    }

    private getChildInterests(userId: number): string[] {
        return ['games', 'videos'];
    }

    private getInternalNotes(userId: number): string {
        return 'Internal analysis notes';
    }

    private assessUserRisk(userId: number): string {
        return 'Medium';
    }

    private calculateDemographicSegment(profile: UserProfile): string {
        return '18-24';
    }

    private clusterUserInterests(interests: string[]): string[] {
        return interests;
    }

    private analyzeBehavioralPatterns(behaviors: BehaviorLog[]): any {
        return {};
    }

    private analyzeLocationPatterns(locations: LocationData[]): any {
        return {};
    }

    private calculateMarketingValue(userId: number): number {
        return 85;
    }
}

// Usage example with violations
const dataService = new DataCollectionService();

// VIOLATION: Processing users without consent
const testUsers = [
    { id: 1, name: 'Alice', age: 12, interests: ['gaming'] },
    { id: 2, name: 'Bob', age: 15, interests: ['music'] },
    { id: 3, name: 'Charlie', age: 25, interests: ['sports'] }
];

testUsers.forEach(user => {
    dataService.collectUserData(user.id, user);
    dataService.trackUserAction(user.id, 'page_view', { page: 'home' });
    dataService.processUserRegistration(user);
});

console.log('Data collection service initialized');
