<!-- components/AppFooter.vue -->
<script setup>
import { ref, computed } from 'vue';
import { 
  Twitter, 
  Github, 
  Linkedin, 
  Heart,
  Sparkles,
  ChevronRight,
  ExternalLink,
  ArrowUpRight
} from 'lucide-vue-next';

const currentYear = computed(() => new Date().getFullYear());
const email = ref('');
const isSubscribing = ref(false);
const showSubscriptionSuccess = ref(false);

const footerLinks = {
  product: [
    { label: 'Features', href: '#'},
    { label: 'Pricing', href: '#' },
    { label: 'Integrations', href: '#', isNew: true },
    { label: 'Updates', href: '#', badge: 'Beta'}
  ],
  company: [
    { label: 'About', href: '#' },
    { label: 'Blog', href: '#' },
    { label: 'Careers', href: '#', badge: 'Hiring'},
    { label: 'Press', href: '#' }
  ],
  support: [
    { label: 'Help Center', href: '#' },
    { label: 'Documentation', href: '#' },
    { label: 'API Reference', href: '#', isExternal: true, badge: 'v2.0' },
    { label: 'Status', href: '#', statusDot: true, statusColor: 'bg-green-400' }
  ]
};

const socialLinks = [
  { 
    icon: Twitter, 
    href: '#', 
    label: 'Twitter',
    color: 'hover:text-blue-400 dark:hover:text-blue-300'
  },
  { 
    icon: Github, 
    href: '#', 
    label: 'GitHub',
    color: 'hover:text-gray-900 dark:hover:text-white'
  },
  { 
    icon: Linkedin, 
    href: '#', 
    label: 'LinkedIn',
    color: 'hover:text-blue-600 dark:hover:text-blue-300'
  },
];

const handleSubscribe = async () => {
  if (!email.value || isSubscribing.value) return;
  
  try {
    isSubscribing.value = true;
    await new Promise(resolve => setTimeout(resolve, 1000));
    showSubscriptionSuccess.value = true;
    email.value = '';
    
    setTimeout(() => {
      showSubscriptionSuccess.value = false;
    }, 3000);
  } finally {
    isSubscribing.value = false;
  }
};
</script>

<template>
  <footer class="bg-white dark:bg-gray-900 border-t border-neutral-100 dark:border-gray-800">
    <div class="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
      <!-- Main Grid Layout -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 text-left">
        <!-- Brand Column -->
        <div class="space-y-6">
          <div class="flex items-center space-x-2">
            <img 
              src="../assets/logo.svg" 
              alt="FlowAgenda" 
              class="w-6 h-6"
            />
            <span class="text-lg font-semibold bg-gradient-to-r from-neutral-600 to-neutral-400 dark:from-neutral-300 dark:to-neutral-500 bg-clip-text text-transparent">
              FlowAgenda
            </span>
          </div>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            Streamline your scheduling with AI-powered event management and seamless calendar integration.
          </p>
          <div class="flex items-center space-x-4">
            <a
              v-for="social in socialLinks"
              :key="social.label"
              :href="social.href"
              :aria-label="social.label"
              class="p-2 text-gray-400 dark:text-gray-500 rounded-lg transition-all duration-200 hover:bg-gray-50 dark:hover:bg-gray-800"
              :class="social.color"
            >
              <component 
                :is="social.icon" 
                class="h-6 w-6"
              />
            </a>
          </div>
        </div>

        <!-- Link Columns -->
        <div 
          v-for="(links, section) in footerLinks" 
          :key="section"
          class="space-y-6"
        >
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider">
            {{ section }}
          </h3>
          <ul class="space-y-4">
            <li v-for="link in links" :key="link.label">
              <a
                :href="link.href"
                class="group inline-flex items-center text-sm text-gray-500 dark:text-gray-400 hover:text-accent-500 dark:hover:text-accent-400 transition-colors"
              >
                <span>{{ link.label }}</span>
                
                <!-- New Badge -->
                <span 
                  v-if="link.isNew"
                  class="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-accent-50 dark:bg-accent-900/30 text-accent-500 dark:text-accent-400"
                >
                  New
                </span>
                
                <!-- Status Badge -->
                <span 
                  v-if="link.badge"
                  class="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                  :class="[
                    link.badge === 'Hiring' 
                      ? 'bg-green-50 dark:bg-green-900/30 text-green-500 dark:text-green-400' 
                      : 'bg-accent-50 dark:bg-accent-900/30 text-accent-500 dark:text-accent-400'
                  ]"
                >
                  {{ link.badge }}
                </span>
                
                <!-- External Link Icon -->
                <ExternalLink 
                  v-if="link.isExternal"
                  class="ml-1 w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity"
                />
                
                <!-- Status Dot -->
                <span 
                  v-if="link.statusDot"
                  class="ml-2 w-2 h-2 rounded-full"
                  :class="link.statusColor"
                />
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Newsletter Section -->
      <div class="mt-12 border-t border-gray-100 dark:border-gray-800 pt-8">
        <div class="rounded-2xl bg-gray-50 dark:bg-gray-800 p-6 lg:p-8 relative overflow-hidden">
          <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between relative z-10">
            <div class="mb-6 lg:mb-0">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                Stay up to date
                <Sparkles class="w-5 h-5 text-accent-400 dark:text-accent-300" />
              </h3>
              <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
                Get notified about new features and updates.
              </p>
            </div>
            <div class="flex flex-col sm:flex-row gap-3">
              <input
                v-model="email"
                type="email"
                placeholder="Enter your email"
                class="px-4 py-2.5 text-sm bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-accent-400 dark:focus:ring-accent-500 focus:border-transparent"
                :disabled="isSubscribing"
              />
              <button 
                @click="handleSubscribe"
                class="inline-flex items-center justify-center px-4 py-2.5 text-sm font-medium text-white bg-accent-400 dark:bg-accent-500 rounded-lg hover:bg-accent-500 dark:hover:bg-accent-600 transition-colors disabled:opacity-75"
                :disabled="isSubscribing || !email"
              >
                <span v-if="isSubscribing">Subscribing...</span>
                <template v-else>
                  <span>Subscribe</span>
                  <ChevronRight class="ml-2 w-4 h-4" />
                </template>
              </button>
            </div>
          </div>

          <!-- Success Message -->
          <transition
            enter-active-class="transition-all duration-300"
            enter-from-class="opacity-0 translate-y-4"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition-all duration-300"
            leave-from-class="opacity-100"
            leave-to-class="opacity-0"
          >
            <div
              v-show="showSubscriptionSuccess"
              class="absolute inset-0 flex items-center justify-center bg-green-500 dark:bg-green-600 bg-opacity-95"
            >
              <div class="text-center text-white">
                <Sparkles class="w-6 h-6 mx-auto mb-2" />
                <p class="font-medium">Thanks for subscribing!</p>
              </div>
            </div>
          </transition>
          
          <!-- Background Pattern -->
          <div class="absolute inset-0 opacity-10 dark:opacity-5">
            <svg class="w-full h-full" viewBox="0 0 80 80" fill="none">
              <path
                d="M14.5 20.5L20.5 14.5M40 8V2M65.5 20.5L59.5 14.5M72 40H78M65.5 59.5L59.5 65.5M40 72V78M14.5 59.5L20.5 65.5M8 40H2"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
              />
            </svg>
          </div>
        </div>
      </div>

      <!-- Bottom Bar -->
      <div class="mt-8 pt-8 border-t border-gray-100 dark:border-gray-800">
        <div class="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <div class="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
            <span>Made with</span>
            <Heart class="w-4 h-4 text-red-400 dark:text-red-300" />
            <span>by FlowAgenda Team • © {{ currentYear }}</span>
          </div>
          <div class="flex items-center space-x-6 text-sm text-gray-500 dark:text-gray-400">
            <a href="#" class="hover:text-accent-500 dark:hover:text-accent-400 transition-colors">Terms</a>
            <a href="#" class="hover:text-accent-500 dark:hover:text-accent-400 transition-colors">Privacy</a>
            <a href="#" class="hover:text-accent-500 dark:hover:text-accent-400 transition-colors">Cookies</a>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.link-hover-animation {
  @apply relative;
}

.link-hover-animation::after {
  @apply absolute bottom-0 left-0 w-0 h-0.5 bg-accent-400 dark:bg-accent-500 transition-all duration-300;
  content: '';
}

.link-hover-animation:hover::after {
  @apply w-full;
}

.newsletter-pattern {
  mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 50%, transparent);
}
</style>