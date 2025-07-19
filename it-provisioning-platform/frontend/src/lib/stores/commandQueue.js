import { writable } from 'svelte/store';
import { browser } from '$app/environment';

// Get the value from localStorage if it exists, otherwise use an empty array
const storedQueue = browser ? JSON.parse(localStorage.getItem('commandQueue') || '[]') : [];

// Create a writable store
const queue = writable(storedQueue);

// Subscribe to changes in the store and update localStorage
queue.subscribe((value) => {
	if (browser) {
		localStorage.setItem('commandQueue', JSON.stringify(value));
	}
});

export const commandQueue = queue;
