import { writable } from 'svelte/store';

// Get the value from localStorage if it exists, otherwise use an empty array
const storedQueue = JSON.parse(localStorage.getItem('commandQueue')) || [];

// Create a writable store
const queue = writable(storedQueue);

// Subscribe to changes in the store and update localStorage
queue.subscribe((value) => {
	localStorage.setItem('commandQueue', JSON.stringify(value));
});

export const commandQueue = queue;
