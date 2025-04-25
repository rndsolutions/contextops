<script>
	import { onMount } from 'svelte';

	import { getSessionUser } from '$lib/apis/auths';
	import { getUserById } from '$lib/apis/users';
	import { WEBUI_BASE_URL } from '$lib/constants';

	let trialPeriod = 0; // Default value

	async function fetchTrialPeriod() {
		try {
			const response = await fetch(WEBUI_BASE_URL + '/api/config/trial-period');
			if (!response.ok) {
				throw new Error('Network response was not ok');
			}
			const data = await response.json();
			trialPeriod = data.trial_period;
			return trialPeriod;
		} catch (error) {
			console.error('Failed to fetch trial period:', error);
		}
	}

	let isVisible = true;
	let remainingDays = 0;

	const MS_PER_DAY = 86400000;
	async function calculateRemainingDays(user) {
		if (!user || !user.created_at || typeof user.trial_extension_days !== 'number') {
			throw new Error('Invalid user object');
		}
    const now = new Date();
    // created_at is in seconds, convert to milliseconds
    const createdAt = new Date(user.created_at * 1000);
    
    const extendedTrial = trialPeriod + (user.trial_extension_days || 0);
    const trialEndTime = createdAt.getTime() + (extendedTrial * MS_PER_DAY);
    const remainingTicks = Math.max(trialEndTime - now.getTime(), 0);
    const remainingDays = Math.floor(remainingTicks / MS_PER_DAY); // Or use Math.round / Math.ceil

    return  remainingDays;
	}

	// Fetch user data and calculate remaining trial days
	onMount(async () => {
		try {
			const usr = await getSessionUser(localStorage.token);
      await fetchTrialPeriod();
			console.log('User:', usr);
			remainingDays = await calculateRemainingDays(usr);
			// Keep popup always visible, so no change to isVisible
		} catch (error) {
			console.error('Failed to fetch user info:', error);
		}
	});

	function closePopup() {
		isVisible = false;
	}
</script>

	<div
		class="fixed bottom-4 right-4 bg-white shadow-lg rounded-lg p-4 flex flex-col items-center z-50"
	>
		<p class="text-gray-800 mb-4 text-center">
			{#if remainingDays > 0}
				🎉 Your trial ends in <strong>{remainingDays}</strong> days! 🎉
			{:else}
				Your trial has ended. Please upgrade to continue.
			{/if}
		</p>
		<button
			id="upgrade-btn"
			class="bg-gradient-to-r from-blue-500 to-green-500 text-white px-5 py-3 rounded-full hover:from-blue-600 hover:to-green-600 transition"
		>
			Upgrade Now
		</button>
	</div>

<style>
	.fixed {
		position: fixed;
	}
	.bottom-4 {
		bottom: 1rem;
	}
	.right-4 {
		right: 1rem;
	}
	.bg-white {
		background-color: white;
	}
	.shadow-lg {
		box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
	}
	.rounded-lg {
		border-radius: 0.5rem;
	}
	.p-4 {
		padding: 1rem;
	}
	.absolute {
		position: absolute;
	}
	.top-1 {
		top: 0.25rem;
	}
	.right-1 {
		right: 0.25rem;
	}
	.text-gray-500 {
		color: #6b7280;
	}
	.hover\:text-gray-700:hover {
		color: #374151;
	}
	.bg-gradient-to-r {
		background-image: linear-gradient(to right, var(--tw-gradient-stops));
	}
	.from-blue-500 {
		--tw-gradient-from: #3b82f6;
		--tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to, rgba(59, 130, 246, 0));
	}
	.to-green-500 {
		--tw-gradient-to: #10b981;
	}
	.hover\:from-blue-600:hover {
		--tw-gradient-from: #2563eb;
	}
	.hover\:to-green-600:hover {
		--tw-gradient-to: #059669;
	}
	.text-white {
		color: white;
	}
	.px-5 {
		padding-left: 1.25rem;
		padding-right: 1.25rem;
	}
	.py-3 {
		padding-top: 0.75rem;
		padding-bottom: 0.75rem;
	}
	.rounded-full {
		border-radius: 9999px;
	}
	.transition {
		transition: all 0.2s;
	}
</style>
