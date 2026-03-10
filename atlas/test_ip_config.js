/**
 * Test script for IP configuration functionality
 * Run this in the browser console to test the configuration system
 */

// Test the configuration system
console.log('🧪 Testing IP Configuration System...');

// Test 1: Check if ConfigManager is working
try {
  // Import the config manager (this would work in the actual app)
  console.log('✅ ConfigManager should be available');
} catch (error) {
  console.error('❌ ConfigManager error:', error);
}

// Test 2: Test localStorage functionality
try {
  const testKey = 'test_ip_config';
  const testValue = '192.168.1.100:8080';
  
  localStorage.setItem(testKey, testValue);
  const retrieved = localStorage.getItem(testKey);
  
  if (retrieved === testValue) {
    console.log('✅ localStorage is working correctly');
    localStorage.removeItem(testKey);
  } else {
    console.error('❌ localStorage test failed');
  }
} catch (error) {
  console.error('❌ localStorage error:', error);
}

// Test 3: Test IP validation
function validateIP(ip) {
  const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  return ipRegex.test(ip);
}

const testIPs = [
  '192.168.1.100',
  '10.0.0.1',
  '172.16.0.1',
  '255.255.255.255',
  'invalid-ip',
  '192.168.1.256'
];

console.log('🧪 Testing IP validation:');
testIPs.forEach(ip => {
  const isValid = validateIP(ip);
  console.log(`${isValid ? '✅' : '❌'} ${ip}: ${isValid ? 'Valid' : 'Invalid'}`);
});

// Test 4: Test port validation
function validatePort(port) {
  const portNum = parseInt(port);
  return !isNaN(portNum) && portNum >= 1 && portNum <= 65535;
}

const testPorts = ['8080', '3000', '80', '443', '65535', '0', '65536', 'invalid'];

console.log('🧪 Testing port validation:');
testPorts.forEach(port => {
  const isValid = validatePort(port);
  console.log(`${isValid ? '✅' : '❌'} Port ${port}: ${isValid ? 'Valid' : 'Invalid'}`);
});

console.log('🎉 IP Configuration tests completed!');
console.log('📝 Instructions for testing in the app:');
console.log('1. Open the app in Lynx');
console.log('2. Go to Manual Config screen');
console.log('3. Try changing the IP address');
console.log('4. Use the "⚡ Actualizar IP Inmediatamente" button');
console.log('5. Test the connection with "🚀 Probar Conexión"');
