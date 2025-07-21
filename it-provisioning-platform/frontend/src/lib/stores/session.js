import { writable } from 'svelte/store';

// We'll simulate login by setting the user ID in localStorage.
const storedUserId = typeof window !== 'undefined' ? localStorage.getItem('sessionUserId') : null;

// Create a writable store for the user object.
export const user = writable(null);

// Function to simulate login
export async function login(userId) {
    if (!userId) {
        logout();
        return;
    }
    try {
        const response = await fetch(`/api/users/${userId}`);
        if (!response.ok) throw new Error("User not found");
        const userData = await response.json();
        user.set(userData);
        if (typeof window !== 'undefined') {
            localStorage.setItem('sessionUserId', userId);
        }
    } catch (error) {
        console.error("Login failed:", error);
        logout();
    }
}

// Function to simulate logout
export function logout() {
    user.set(null);
    if (typeof window !== 'undefined') {
        localStorage.removeItem('sessionUserId');
    }
}

// Automatically log in if a user ID is found in storage (only in browser)
if (typeof window !== 'undefined' && storedUserId) {
    login(storedUserId);
}
