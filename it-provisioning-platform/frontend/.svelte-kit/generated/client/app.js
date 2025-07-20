export { matchers } from './matchers.js';

export const nodes = [
	() => import('./nodes/0'),
	() => import('./nodes/1'),
	() => import('./nodes/2'),
	() => import('./nodes/3'),
	() => import('./nodes/4'),
	() => import('./nodes/5'),
	() => import('./nodes/6'),
	() => import('./nodes/7'),
	() => import('./nodes/8'),
	() => import('./nodes/9'),
	() => import('./nodes/10'),
	() => import('./nodes/11'),
	() => import('./nodes/12'),
	() => import('./nodes/13'),
	() => import('./nodes/14'),
	() => import('./nodes/15'),
	() => import('./nodes/16'),
	() => import('./nodes/17')
];

export const server_loads = [];

export const dictionary = {
		"/": [2],
		"/admin/analytics": [3],
		"/admin/audit": [4],
		"/admin/dashboard": [5],
		"/admin/forms": [6],
		"/admin/forms/builder": [7],
		"/admin/forms/[id]": [8],
		"/admin/initialize": [9],
		"/admin/new-user": [10],
		"/admin/temp-accounts": [11],
		"/requests": [12],
		"/requests/new": [13],
		"/requests/[id]": [14],
		"/shared-mailboxes": [15],
		"/test-api": [16],
		"/users": [17]
	};

export const hooks = {
	handleError: (({ error }) => { console.error(error) }),
	
	reroute: (() => {}),
	transport: {}
};

export const decoders = Object.fromEntries(Object.entries(hooks.transport).map(([k, v]) => [k, v.decode]));

export const hash = false;

export const decode = (type, value) => decoders[type](value);

export { default as root } from '../root.svelte';