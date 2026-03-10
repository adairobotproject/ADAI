/**
 * Request Manager Service
 * Prevents multiple simultaneous requests to the same endpoint
 */

class RequestManager {
  constructor() {
    this.activeRequests = new Map()
  }

  /**
   * Execute a request with deduplication
   * @param {string} key - Unique key for the request
   * @param {Function} requestFn - Function that returns a Promise
   * @returns {Promise} Request result
   */
  async executeRequest(key, requestFn) {
    // If there's already an active request for this key, return the existing promise
    if (this.activeRequests.has(key)) {
      console.log(`Request ${key} already in progress, returning existing promise`)
      return this.activeRequests.get(key)
    }

    // Create new request
    const requestPromise = requestFn()
      .finally(() => {
        // Clean up when request completes
        this.activeRequests.delete(key)
      })

    // Store the promise
    this.activeRequests.set(key, requestPromise)
    
    return requestPromise
  }

  /**
   * Check if a request is currently active
   * @param {string} key - Request key
   * @returns {boolean} True if request is active
   */
  isRequestActive(key) {
    return this.activeRequests.has(key)
  }

  /**
   * Cancel a specific request
   * @param {string} key - Request key
   */
  cancelRequest(key) {
    this.activeRequests.delete(key)
  }

  /**
   * Cancel all active requests
   */
  cancelAllRequests() {
    this.activeRequests.clear()
  }

  /**
   * Get count of active requests
   * @returns {number} Number of active requests
   */
  getActiveRequestCount() {
    return this.activeRequests.size
  }
}

// Create singleton instance
const requestManager = new RequestManager()

export default requestManager
