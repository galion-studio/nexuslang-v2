// Package proxy provides HTTP reverse proxy functionality
package proxy

import (
	"io"
	"net/http"
	"strings"
	"time"

	"nexus-api-gateway/pkg/logger"
)

// ServiceProxy handles proxying requests to backend services
type ServiceProxy struct {
	client *http.Client
	logger *logger.Logger
}

// NewServiceProxy creates a new service proxy
func NewServiceProxy(log *logger.Logger) *ServiceProxy {
	return &ServiceProxy{
		client: &http.Client{
			Timeout: 30 * time.Second, // 30 second timeout
		},
		logger: log,
	}
}

// ProxyRequest forwards a request to a backend service
func (sp *ServiceProxy) ProxyRequest(w http.ResponseWriter, r *http.Request, targetURL string) {
	// Build the target URL
	// Remove the route prefix and append the rest of the path
	targetPath := r.URL.Path
	fullURL := targetURL + targetPath
	if r.URL.RawQuery != "" {
		fullURL += "?" + r.URL.RawQuery
	}
	
	sp.logger.Debug("Proxying %s %s to %s", r.Method, r.URL.Path, fullURL)
	
	// Create new request
	proxyReq, err := http.NewRequest(r.Method, fullURL, r.Body)
	if err != nil {
		sp.logger.Error("Failed to create proxy request: %v", err)
		http.Error(w, "internal server error", http.StatusInternalServerError)
		return
	}
	
	// Copy headers from original request
	copyHeaders(r.Header, proxyReq.Header)
	
	// Send request to backend service
	resp, err := sp.client.Do(proxyReq)
	if err != nil {
		sp.logger.Error("Backend request failed: %v", err)
		http.Error(w, "service unavailable", http.StatusServiceUnavailable)
		return
	}
	defer resp.Body.Close()
	
	// Copy response headers
	copyHeaders(resp.Header, w.Header())
	
	// Set status code
	w.WriteHeader(resp.StatusCode)
	
	// Copy response body
	_, err = io.Copy(w, resp.Body)
	if err != nil {
		sp.logger.Error("Failed to copy response body: %v", err)
	}
}

// copyHeaders copies HTTP headers from source to destination
func copyHeaders(src, dst http.Header) {
	for key, values := range src {
		// Skip hop-by-hop headers
		if isHopByHopHeader(key) {
			continue
		}
		
		for _, value := range values {
			dst.Add(key, value)
		}
	}
}

// isHopByHopHeader checks if a header is hop-by-hop
// These headers should not be forwarded
func isHopByHopHeader(header string) bool {
	hopByHopHeaders := []string{
		"Connection",
		"Keep-Alive",
		"Proxy-Authenticate",
		"Proxy-Authorization",
		"Te",
		"Trailers",
		"Transfer-Encoding",
		"Upgrade",
	}
	
	headerLower := strings.ToLower(header)
	for _, h := range hopByHopHeaders {
		if strings.ToLower(h) == headerLower {
			return true
		}
	}
	
	return false
}

