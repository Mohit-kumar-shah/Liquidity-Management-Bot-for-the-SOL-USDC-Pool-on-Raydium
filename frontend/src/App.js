import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Play, Pause, RefreshCw, Wallet, DollarSign, Activity, AlertCircle, CheckCircle, Clock, TrendingUp } from 'lucide-react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [botStatus, setBotStatus] = useState(null);
  const [positions, setPositions] = useState([]);
  const [logs, setLogs] = useState([]);
  const [walletInfo, setWalletInfo] = useState(null);
  const [currentPrice, setCurrentPrice] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [statusRes, positionsRes, logsRes, walletRes, priceRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/status`),
        axios.get(`${API_BASE_URL}/api/positions?status=active`),
        axios.get(`${API_BASE_URL}/api/logs?limit=50`),
        axios.get(`${API_BASE_URL}/api/wallet`),
        axios.get(`${API_BASE_URL}/api/price`)
      ]);
      
      setBotStatus(statusRes.data);
      setPositions(positionsRes.data);
      setLogs(logsRes.data);
      setWalletInfo(walletRes.data);
      setCurrentPrice(priceRes.data);
    } catch (err) {
      setError('Failed to fetch data');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const startBot = async () => {
    try {
      setLoading(true);
      await axios.post(`${API_BASE_URL}/api/start`);
      await fetchData();
    } catch (err) {
      setError('Failed to start bot');
      console.error('Error starting bot:', err);
    } finally {
      setLoading(false);
    }
  };

  const stopBot = async () => {
    try {
      setLoading(true);
      await axios.post(`${API_BASE_URL}/api/stop`);
      await fetchData();
    } catch (err) {
      setError('Failed to stop bot');
      console.error('Error stopping bot:', err);
    } finally {
      setLoading(false);
    }
  };

  const testNotification = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/test-notification`);
      alert('Test notification sent!');
    } catch (err) {
      setError('Failed to send test notification');
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 4
    }).format(price);
  };

  const formatBalance = (balance, symbol) => {
    return `${parseFloat(balance).toFixed(4)} ${symbol}`;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'closed': return 'text-gray-600 bg-gray-100';
      case 'out_of_range': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getLogLevelColor = (level) => {
    switch (level) {
      case 'INFO': return 'text-blue-600 bg-blue-100';
      case 'WARNING': return 'text-yellow-600 bg-yellow-100';
      case 'ERROR': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center justify-center gap-3">
            <Activity className="text-purple-400" />
            Solana Liquidity Management Bot
          </h1>
          <p className="text-purple-200">Automated SOL-USDC liquidity management on Raydium</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/20 border border-red-500/30 rounded-lg text-red-200 flex items-center gap-2">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Bot Status */}
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 border border-white/20">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Bot Status</h3>
              {botStatus?.is_running ? (
                <div className="flex items-center gap-2 text-green-400">
                  <CheckCircle size={20} />
                  <span>Running</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-red-400">
                  <AlertCircle size={20} />
                  <span>Stopped</span>
                </div>
              )}
            </div>
            <div className="flex gap-2">
              <button
                onClick={botStatus?.is_running ? stopBot : startBot}
                disabled={loading || !walletInfo?.configured}
                className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                  botStatus?.is_running
                    ? 'bg-red-500/20 text-red-300 hover:bg-red-500/30 border border-red-500/30'
                    : 'bg-green-500/20 text-green-300 hover:bg-green-500/30 border border-green-500/30'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {botStatus?.is_running ? <Pause size={16} /> : <Play size={16} />}
                {botStatus?.is_running ? 'Stop' : 'Start'}
              </button>
              <button
                onClick={fetchData}
                disabled={loading}
                className="px-3 py-2 bg-purple-500/20 text-purple-300 hover:bg-purple-500/30 border border-purple-500/30 rounded-lg transition-all disabled:opacity-50"
              >
                <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
              </button>
            </div>
          </div>

          {/* Current Price */}
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 border border-white/20">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-white">SOL Price</h3>
              <TrendingUp className="text-purple-400" size={20} />
            </div>
            <div className="text-2xl font-bold text-purple-300">
              {currentPrice ? formatPrice(currentPrice.sol_price) : 'Loading...'}
            </div>
            <p className="text-sm text-gray-400 mt-1">
              Last updated: {currentPrice ? new Date(currentPrice.timestamp).toLocaleTimeString() : ''}
            </p>
          </div>

          {/* Wallet Info */}
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 border border-white/20">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-white">Wallet</h3>
              <Wallet className="text-purple-400" size={20} />
            </div>
            {walletInfo?.configured ? (
              <div className="space-y-1">
                <div className="text-sm text-gray-300">
                  SOL: {formatBalance(walletInfo.sol_balance, 'SOL')}
                </div>
                <div className="text-sm text-gray-300">
                  USDC: {formatBalance(walletInfo.usdc_balance, 'USDC')}
                </div>
              </div>
            ) : (
              <div className="text-red-400 text-sm">Wallet not configured</div>
            )}
          </div>

          {/* Active Positions */}
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 border border-white/20">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-white">Positions</h3>
              <DollarSign className="text-purple-400" size={20} />
            </div>
            <div className="text-2xl font-bold text-purple-300">
              {botStatus?.active_positions || 0}
            </div>
            <p className="text-sm text-gray-400">Active liquidity positions</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Positions Table */}
          <div className="bg-white/10 backdrop-blur-md rounded-lg border border-white/20 overflow-hidden">
            <div className="p-6 border-b border-white/20">
              <h3 className="text-xl font-semibold text-white">Liquidity Positions</h3>
            </div>
            <div className="overflow-x-auto max-h-96">
              {positions.length > 0 ? (
                <table className="w-full">
                  <thead className="bg-white/5">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Position</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Range</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Amounts</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/10">
                    {positions.map((position) => (
                      <tr key={position.id} className="hover:bg-white/5">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                          {position.position_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                          {formatPrice(position.lower_price)} - {formatPrice(position.upper_price)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                          <div>{formatBalance(position.sol_amount, 'SOL')}</div>
                          <div>{formatBalance(position.usdc_amount, 'USDC')}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(position.status)}`}>
                            {position.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="p-6 text-center text-gray-400">No active positions</div>
              )}
            </div>
          </div>

          {/* Activity Logs */}
          <div className="bg-white/10 backdrop-blur-md rounded-lg border border-white/20 overflow-hidden">
            <div className="p-6 border-b border-white/20 flex items-center justify-between">
              <h3 className="text-xl font-semibold text-white">Activity Logs</h3>
              <button
                onClick={testNotification}
                className="px-3 py-1 bg-purple-500/20 text-purple-300 hover:bg-purple-500/30 border border-purple-500/30 rounded text-sm transition-all"
              >
                Test Discord
              </button>
            </div>
            <div className="overflow-y-auto max-h-96">
              {logs.length > 0 ? (
                <div className="space-y-1 p-4">
                  {logs.map((log) => (
                    <div key={log.id} className="flex items-start gap-3 p-3 hover:bg-white/5 rounded-lg">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getLogLevelColor(log.level)}`}>
                        {log.level}
                      </span>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm text-gray-300">{log.message}</div>
                        <div className="text-xs text-gray-500 flex items-center gap-1 mt-1">
                          <Clock size={12} />
                          {new Date(log.timestamp).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-6 text-center text-gray-400">No logs available</div>
              )}
            </div>
          </div>
        </div>

        {/* Configuration Notice */}
        {!walletInfo?.configured && (
          <div className="mt-8 p-6 bg-yellow-500/20 border border-yellow-500/30 rounded-lg">
            <div className="flex items-center gap-2 text-yellow-300 mb-2">
              <AlertCircle size={20} />
              <span className="font-semibold">Configuration Required</span>
            </div>
            <p className="text-yellow-200">
              Please configure your wallet private key, Discord webhook, and other settings in the .env file before starting the bot.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
