type LogLevel = 'info' | 'warn' | 'error' | 'debug';

interface LogPayload {
  level: LogLevel;
  message: string;
  context?: Record<string, any>;
}

class Logger {
  private async sendLog(payload: LogPayload) {
    try {
      // In Next.js, API URL might be relative if proxying, or we might need the full URL from env
      // Using relative path assuming API is under /api proxy or same domain.
      // Adjust if your frontend and backend run on different domains without proxy.
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api';
      
      const response = await fetch(`${apiUrl}/v1/logs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
        // Don't wait for the response or throw if it fails (avoids infinite error loops)
        keepalive: true,
      });
      
      if (!response.ok) {
        console.error('Failed to send log to backend:', response.statusText);
      }
    } catch (e) {
      // Fallback to console if network request fails, avoid recursive logging
      console.error('Failed to send log to backend:', e);
    }
  }

  info(message: string, context?: Record<string, any>) {
    console.info(message, context || '');
    this.sendLog({ level: 'info', message, context });
  }

  warn(message: string, context?: Record<string, any>) {
    console.warn(message, context || '');
    this.sendLog({ level: 'warn', message, context });
  }

  error(message: string | Error, context?: Record<string, any>) {
    console.error(message, context || '');
    
    let msg = typeof message === 'string' ? message : message.message;
    let enhancedContext = { ...context };
    
    if (message instanceof Error) {
      enhancedContext.stack = message.stack;
      enhancedContext.name = message.name;
    }

    this.sendLog({ level: 'error', message: msg, context: enhancedContext });
  }

  debug(message: string, context?: Record<string, any>) {
    console.debug(message, context || '');
    // Usually we might not want to send debug logs to backend in prod, 
    // but the user wants EVERYTHING. We can send it.
    this.sendLog({ level: 'debug', message, context });
  }
}

export const logger = new Logger();
