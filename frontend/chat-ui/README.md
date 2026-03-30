# AI Banking Chatbot - Modern Frontend

A professional, modern fintech chatbot interface built with Next.js 16, Tailwind CSS, and TypeScript.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ installed
- Backend API running on `http://127.0.0.1:8000`

### Installation

```bash
cd frontend/chat-ui
npm install
```

### Run Development Server

```bash
npm run dev
```

The app will start at `http://localhost:3000`

## ✨ Features

### Professional UI/UX
- **Modern Fintech Design** - Clean, professional banking aesthetic
- **Responsive Layout** - Works perfectly on all screen sizes
- **Smooth Animations** - Powered by Framer Motion
- **Dark Mode** - Full dark mode support with localStorage persistence
- **Bilingual Support** - English and Arabic (RTL) support

### Chat Interface
- **Sidebar** - Collapsible chat history panel
- **Message Bubbles** - Styled user and assistant messages
- **Quick Actions** - Pre-defined common queries
- **Typing Indicator** - Animated dots while AI is responding
- **Language Detection** - Automatic language badges on messages

### Technical Features
- **Tailwind CSS** - Fully configured utility-first CSS
- **TypeScript** - Type-safe code
- **Axios** - HTTP client for API calls
- **Date Formatting** - Professional timestamp display
- **Error Handling** - Graceful error messages

## 🎨 Design System

### Color Palette
- **Primary Blue**: `#2563eb` to `#1d4ed8`
- **Background**: Light gray to white gradient
- **Dark Mode**: Deep blue-gray tones
- **Accents**: Professional banking colors

### Typography
- Clean, readable sans-serif fonts
- Proper hierarchy and spacing
- RTL support for Arabic

### Components
- Rounded chat bubbles with shadows
- Gradient backgrounds
- Smooth transitions
- Hover effects

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### Tailwind Configuration

Located in `tailwind.config.js`:
- Dark mode: `class` strategy
- Custom color palette
- Extended theme settings

### API Integration

The frontend connects to the backend via:

```typescript
POST http://127.0.0.1:8000/chat
{
  "message": "user input"
}

Response:
{
  "answer": "AI response",
  "language": "Arabic/English",
  "confidence": 0.95,
  "conversation_id": "uuid"
}
```

## 📁 Project Structure

```
chat-ui/
├── app/
│   ├── globals.css       # Global styles with Tailwind
│   ├── layout.tsx        # Root layout
│   ├── page.tsx          # Main chat page
│   └── favicon.svg       # App icon
├── public/               # Static assets
├── .env.local            # Environment variables
├── tailwind.config.js    # Tailwind configuration
├── postcss.config.mjs    # PostCSS configuration
└── package.json          # Dependencies
```

## 🎯 Key Components

### 1. Sidebar
- Shows chat history
- New chat button
- Clear all functionality
- Collapsible design

### 2. Header
- App branding
- Language toggle (EN/AR)
- Dark mode toggle
- Menu button

### 3. Chat Area
- Welcome screen with quick actions
- Message bubbles (user/assistant)
- Typing indicator
- Auto-scroll to bottom

### 4. Input Bar
- Text input field
- Send button
- Disabled state handling
- Helper text

## 🌙 Dark Mode

Dark mode is implemented using Tailwind's class strategy:

1. Toggle button updates `document.documentElement.classList`
2. Preference saved to `localStorage`
3. Persists across sessions
4. Respects system preference on first load

## 🌐 Internationalization

### Supported Languages
- English (LTR)
- Arabic (RTL)

### Implementation
- Language state management
- Dynamic text direction
- Localized UI strings
- Language badges on messages

## 🚨 Error Handling

The app handles errors gracefully:
- Network errors show user-friendly messages
- Loading states prevent duplicate sends
- Typing indicators show processing
- Fallback messages for server errors

## 📱 Responsive Design

Breakpoints:
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

The layout adapts:
- Sidebar becomes overlay on mobile
- Grid columns adjust automatically
- Touch-friendly buttons

## 🔒 Best Practices

### Code Quality
- TypeScript for type safety
- ESLint configuration
- Proper component structure
- Clean separation of concerns

### Performance
- Client-side rendering with 'use client'
- Optimized animations
- Efficient re-renders
- Lazy loading where applicable

### Accessibility
- Semantic HTML
- ARIA labels where needed
- Keyboard navigation support
- High contrast ratios

## 🛠️ Development Commands

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint
```

## 🎨 UI Preview

### Welcome Screen
- Animated logo
- Welcome message
- 5 quick action buttons
- Clean, inviting design

### Chat Screen
- Professional header
- Message history
- Styled chat bubbles
- Real-time typing indicator

### Dark Mode
- Instant theme switch
- Smooth transitions
- Consistent color scheme
- Eye-friendly dark colors

## 📊 State Management

Using React hooks:
- `useState` - Messages, input, UI states
- `useEffect` - Side effects, subscriptions
- `useRef` - DOM references
- Context not needed for this scale

## 🔄 Future Enhancements

Potential improvements:
- Conversation history persistence
- Export chat functionality
- Voice input support
- File upload support
- Multi-session management
- Analytics dashboard

## 🐛 Troubleshooting

### Tailwind Not Working
- Check `tailwind.config.js` content paths
- Verify `globals.css` imports
- Restart dev server

### Dark Mode Not Persisting
- Check localStorage in browser
- Verify `suppressHydrationWarning` on html tag
- Clear cache and reload

### API Connection Failed
- Verify backend is running
- Check `.env.local` configuration
- Inspect browser console for CORS issues

## ✅ Validation Checklist

Before deployment, ensure:
- [ ] Tailwind CSS working properly
- [ ] Dark mode toggles and persists
- [ ] All animations smooth
- [ ] API integration functional
- [ ] Responsive on all devices
- [ ] No console errors
- [ ] TypeScript compiles without errors
- [ ] Production build successful

## 📞 Support

For issues or questions about this frontend implementation, refer to the project documentation or contact the development team.

---

**Built with ❤️ using Next.js, Tailwind CSS, and TypeScript**
