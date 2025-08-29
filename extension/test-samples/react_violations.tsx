// Sample React component with compliance violations
// This demonstrates frontend privacy violations

import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface UserData {
    id: number;
    name: string;
    email: string;
    age: number;
    location: string;
}

const UserTrackingComponent: React.FC = () => {
    const [userData, setUserData] = useState<UserData | null>(null);
    const [locationData, setLocationData] = useState<any>(null);
    const [behaviorLog, setBehaviorLog] = useState<any[]>([]);

    // VIOLATION: Collecting user data without consent on component mount
    useEffect(() => {
        collectUserData();
        trackUserLocation();
        startBehaviorTracking();
    }, []);

    // VIOLATION: Collecting personal data without explicit consent
    const collectUserData = async () => {
        try {
            // VIOLATION: Making API calls without user consent
            const response = await axios.get('/api/user/profile');

            const data = response.data;
            setUserData(data);

            // VIOLATION: Sharing data with third parties
            shareWithAnalytics(data);
            shareWithAdvertising(data);

        } catch (error) {
            console.error('Failed to collect user data:', error);
        }
    };

    // VIOLATION: Location tracking without proper consent
    const trackUserLocation = () => {
        if (navigator.geolocation) {
            navigator.geolocation.watchPosition(
                (position) => {
                    const location = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: new Date().toISOString(),
                        userId: userData?.id
                    };

                    setLocationData(location);

                    // VIOLATION: Sending location to multiple third parties
                    sendLocationToPartners(location);
                },
                (error) => console.error('Location tracking error:', error),
                { enableHighAccuracy: true, maximumAge: 30000 }
            );
        }
    };

    // VIOLATION: Sharing location with advertising partners
    const sendLocationToPartners = (location: any) => {
        const partners = [
            'facebook.com',
            'google-analytics.com',
            'tiktok.com',
            'ad-network.com'
        ];

        partners.forEach(partner => {
            axios.post(`https://${partner}/location-track`, location);
        });
    };

    // VIOLATION: Behavioral tracking without consent
    const startBehaviorTracking = () => {
        const trackEvent = (event: string, element: string) => {
            const eventData = {
                event: event,
                element: element,
                timestamp: new Date().toISOString(),
                url: window.location.href,
                userAgent: navigator.userAgent,
                sessionId: getSessionId(),
                userId: userData?.id
            };

            setBehaviorLog(prev => [...prev, eventData]);

            // VIOLATION: Real-time event sending
            sendEventToAnalytics(eventData);
        };

        // VIOLATION: Tracking all user interactions
        document.addEventListener('click', (e) => {
            trackEvent('click', (e.target as HTMLElement).tagName);
        });

        document.addEventListener('scroll', () => {
            trackEvent('scroll', 'window');
        });

        document.addEventListener('keydown', (e) => {
            trackEvent('keydown', e.key);
        });
    };

    // VIOLATION: Sharing data with analytics without consent
    const shareWithAnalytics = (data: UserData) => {
        axios.post('/api/analytics/user-profile', {
            ...data,
            consent: false,
            timestamp: new Date().toISOString()
        });
    };

    // VIOLATION: Sharing data with advertising networks
    const shareWithAdvertising = (data: UserData) => {
        const adNetworks = [
            'facebook-ads.com',
            'google-ads.com',
            'tiktok-marketing.com'
        ];

        adNetworks.forEach(network => {
            axios.post(`https://${network}/user-profile`, {
                userId: data.id,
                interests: extractInterests(data),
                demographics: {
                    age: data.age,
                    location: data.location
                }
            });
        });
    };

    const extractInterests = (data: UserData): string[] => {
        // VIOLATION: Inferring interests from user data
        const interests: string[] = [];

        if (data.name.toLowerCase().includes('sport')) interests.push('sports');
        if (data.email.includes('music')) interests.push('music');
        if (data.age < 25) interests.push('youth_content');

        return interests;
    };

    // VIOLATION: Age verification issues
    const handleUserRegistration = (formData: any) => {
        if (formData.age < 13) {
            // VIOLATION: Processing children's data without parental consent
            processChildRegistration(formData);
        } else if (formData.age < 16) {
            // VIOLATION: Insufficient privacy controls for teens
            processTeenRegistration(formData);
        } else {
            // VIOLATION: No consent for adults
            processAdultRegistration(formData);
        }
    };

    // VIOLATION: Collecting children's data
    const processChildRegistration = (childData: any) => {
        const childProfile = {
            ...childData,
            school: getSchoolInfo(childData.id),
            friends: getFriendsList(childData.id),
            interests: getChildInterests(childData.id),
            activityLog: getActivityLog(childData.id)
        };

        axios.post('/api/children/profiles', childProfile);
    };

    // VIOLATION: Device fingerprinting
    const getDeviceFingerprint = (): string => {
        const fingerprint = [
            navigator.userAgent,
            navigator.language,
            screen.width + 'x' + screen.height,
            new Date().getTimezoneOffset(),
            navigator.platform,
            navigator.cookieEnabled
        ].join('|');

        return btoa(fingerprint);
    };

    // VIOLATION: Exporting user data
    const exportUserData = () => {
        if (!userData) return;

        const exportData = {
            ...userData,
            deviceFingerprint: getDeviceFingerprint(),
            behaviorHistory: behaviorLog,
            locationHistory: locationData,
            internalNotes: 'Exported for analysis',
            marketingProfile: createMarketingProfile()
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'user-data-export.json';
        a.click();
    };

    const createMarketingProfile = () => {
        return {
            interests: extractInterests(userData!),
            riskScore: calculateRiskScore(),
            marketingValue: calculateMarketingValue(),
            segments: determineSegments()
        };
    };

    // Helper functions (simplified)
    const getSessionId = (): string => Math.random().toString(36);
    const sendEventToAnalytics = (event: any) => axios.post('/api/analytics/event', event);
    const getSchoolInfo = (id: number) => ({ name: 'Example School' });
    const getFriendsList = (id: number) => [1, 2, 3];
    const getChildInterests = (id: number) => ['games', 'videos'];
    const getActivityLog = (id: number) => [];
    const processTeenRegistration = (data: any) => axios.post('/api/teens/register', data);
    const processAdultRegistration = (data: any) => axios.post('/api/adults/register', data);
    const calculateRiskScore = () => Math.floor(Math.random() * 100);
    const calculateMarketingValue = () => Math.floor(Math.random() * 1000);
    const determineSegments = () => ['high-value', 'active-user'];

    return (
        <div className="user-tracking-component">
            <h2>User Tracking Dashboard</h2>

            {userData && (
                <div className="user-info">
                    <h3>User Information</h3>
                    <p>Name: {userData.name}</p>
                    <p>Email: {userData.email}</p>
                    <p>Age: {userData.age}</p>
                    <p>Location: {userData.location}</p>
                </div>
            )}

            {locationData && (
                <div className="location-info">
                    <h3>Location Tracking</h3>
                    <p>Latitude: {locationData.latitude}</p>
                    <p>Longitude: {locationData.longitude}</p>
                    <p>Accuracy: {locationData.accuracy}m</p>
                </div>
            )}

            <div className="behavior-log">
                <h3>Behavior Log ({behaviorLog.length} events)</h3>
                <button onClick={() => setBehaviorLog([])}>Clear Log</button>
            </div>

            <div className="actions">
                <button onClick={exportUserData}>
                    Export User Data
                </button>
                <button onClick={() => shareWithAnalytics(userData!)}>
                    Share with Analytics
                </button>
            </div>
        </div>
    );
};

export default UserTrackingComponent;
