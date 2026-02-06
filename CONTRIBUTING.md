# Contributing to Perplex Edge

Thank you for your interest in contributing to Perplex Edge! This guide will help you get started.

## 🚀 Quick Start

### For New Contributors

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests** if applicable
5. **Submit a pull request**

### For Existing Contributors

1. **Check the issue tracker** for assigned tasks
2. **Create a branch** from `main`: `git checkout -b feature/issue-123`
3. **Follow the coding standards** below
4. **Ensure all tests pass**
5. **Update documentation** if needed
6. **Submit PR** with detailed description

## 🛠️ Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL (local or via Docker)

### Local Development

```bash
# Clone your fork
git clone https://github.com/your-username/perplex-edge.git
cd perplex-edge

# Set up backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Set up database
alembic upgrade head

# Start backend
uvicorn app.main:app --reload

# Set up frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Docker Development

```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# View logs
docker-compose logs -f
```

## 📝 Coding Standards

### Python (Backend)

#### Code Style
- **Black** for code formatting
- **Ruff** for linting and import sorting
- **MyPy** for type checking
- **PEP 8** compliance

#### Type Hints
```python
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user_picks(
    user_id: int,
    db: AsyncSession,
    limit: int = 10
) -> List[ModelPick]:
    """Get user's betting picks with pagination."""
    result = await db.execute(
        select(ModelPick)
        .where(ModelPick.user_id == user_id)
        .limit(limit)
    )
    return result.scalars().all()
```

#### Error Handling
```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def get_game_odds(game_id: int, db: AsyncSession):
    try:
        result = await db.execute(
            select(Odds).where(Odds.game_id == game_id)
        )
        odds = result.scalars().first()
        
        if not odds:
            raise HTTPException(
                status_code=404,
                detail=f"Odds not found for game {game_id}"
            )
        
        return odds
        
    except Exception as e:
        logger.error(f"Error fetching odds for game {game_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

#### Database Operations
```python
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

async def create_pick(pick_data: PickCreate, db: AsyncSession) -> ModelPick:
    """Create a new betting pick."""
    pick = ModelPick(**pick_data.dict())
    db.add(pick)
    await db.commit()
    await db.refresh(pick)
    return pick

async def update_pick_status(
    pick_id: int, 
    status: str, 
    db: AsyncSession
) -> Optional[ModelPick]:
    """Update pick status."""
    await db.execute(
        update(ModelPick)
        .where(ModelPick.id == pick_id)
        .values(status=status)
    )
    await db.commit()
    
    result = await db.execute(
        select(ModelPick).where(ModelPick.id == pick_id)
    )
    return result.scalars().first()
```

### TypeScript (Frontend)

#### Code Style
- **ESLint** with TypeScript rules
- **Prettier** for formatting
- **Strict TypeScript** configuration

#### Component Structure
```typescript
import React from 'react';
import { useQuery } from '@tanstack/react-query';

interface GameOddsProps {
  gameId: string;
  sportId: number;
}

export const GameOdds: React.FC<GameOddsProps> = ({ gameId, sportId }) => {
  const { data: odds, isLoading, error } = useQuery({
    queryKey: ['game-odds', gameId],
    queryFn: () => fetchGameOdds(gameId, sportId),
  });

  if (isLoading) return <div>Loading odds...</div>;
  if (error) return <div>Error loading odds</div>;

  return (
    <div className="game-odds">
      {/* Odds display */}
    </div>
  );
};
```

#### API Client
```typescript
import { API_BASE_URL } from '../api/client';

export interface GameOdds {
  gameId: string;
  sportId: number;
  odds: OddsData[];
}

export async function fetchGameOdds(
  gameId: string, 
  sportId: number
): Promise<GameOdds> {
  const response = await fetch(
    `${API_BASE_URL}/sports/${sportId}/games/${gameId}/odds`
  );
  
  if (!response.ok) {
    throw new Error(`Failed to fetch odds: ${response.statusText}`);
  }
  
  return response.json();
}
```

## 🧪 Testing

### Backend Tests

#### Unit Tests
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_game_odds():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/sports/1/games/123/odds")
        assert response.status_code == 200
        assert "odds" in response.json()
```

#### Integration Tests
```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.picks_generator import PicksGenerator

@pytest.mark.asyncio
async def test_picks_generator(db: AsyncSession):
    generator = PicksGenerator(db)
    picks = await generator.generate_picks(sport_id=1, limit=10)
    
    assert len(picks) > 0
    assert all(pick.expected_value > 0 for pick in picks)
```

### Frontend Tests

#### Component Tests
```typescript
import { render, screen } from '@testing-library/react';
import { GameOdds } from './GameOdds';

test('displays game odds', () => {
  render(<GameOdds gameId="123" sportId={1} />);
  expect(screen.getByText('Loading odds...')).toBeInTheDocument();
});
```

#### API Tests
```typescript
import { fetchGameOdds } from '../api/odds';

test('fetches game odds successfully', async () => {
  const odds = await fetchGameOdds('123', 1);
  expect(odds).toHaveProperty('gameId', '123');
  expect(odds).toHaveProperty('odds');
});
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Coverage reports
cd backend
pytest --cov=app

cd frontend
npm run test:coverage
```

## 📋 Pull Request Process

### Before Submitting

1. **Code Quality**
   - [ ] Run linting: `ruff check .` and `eslint .`
   - [ ] Run formatting: `black .` and `prettier --write .`
   - [ ] Run type checking: `mypy .` and `tsc --noEmit`

2. **Testing**
   - [ ] All tests pass: `pytest` and `npm test`
   - [ ] Add tests for new features
   - [ ] Update test coverage if needed

3. **Documentation**
   - [ ] Update API docs if endpoints changed
   - [ ] Update README if features added
   - [ ] Add comments to complex code

### PR Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Environment variables documented (if applicable)
```

## 🏷️ Issue Labels

### Type Labels
- `bug`: Bug reports and fixes
- `feature`: New features and enhancements
- `documentation`: Documentation improvements
- `testing`: Test-related issues
- `performance`: Performance optimizations

### Priority Labels
- `critical`: Urgent issues (security, production bugs)
- `high`: Important features/bugs
- `medium`: Nice-to-have improvements
- `low`: Minor issues or future features

### Component Labels
- `backend`: Backend API and services
- `frontend`: React frontend
- `database`: Database schema and migrations
- `deployment`: Docker and deployment configuration
- `documentation`: Docs and guides

## 🔄 Release Process

### Version Management
- Follow [Semantic Versioning](https://semver.org/)
- Update version numbers in `package.json` and `pyproject.toml`
- Update CHANGELOG.md with all changes

### Release Checklist
1. All tests passing
2. Documentation updated
3. Version numbers updated
4. CHANGELOG.md updated
5. Tag created: `git tag v0.1.0`
6. Push tag: `git push origin v0.1.0`

## 🤝 Community Guidelines

### Code of Conduct

1. **Be Respectful**: Treat everyone with respect and kindness
2. **Be Inclusive**: Welcome contributors from all backgrounds
3. **Be Constructive**: Provide helpful feedback and suggestions
4. **Be Patient**: Remember that everyone has different skill levels

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **Discord**: General discussion and questions
- **Email**: security@perplex-edge.com (security issues only)

### Getting Help

1. **Check Documentation**: Look at existing docs first
2. **Search Issues**: Check if your question has been answered
3. **Ask on Discord**: Get help from the community
4. **Create Issue**: For bugs or feature requests

## 🏆 Recognition

### Contributors

All contributors are recognized in:
- README.md contributors section
- Release notes
- Annual contributor highlights

### Types of Contributions

- **Code**: New features, bug fixes, tests
- **Documentation**: Guides, API docs, tutorials
- **Design**: UI/UX improvements, graphics
- **Community**: Support, discussions, feedback
- **Security**: Vulnerability reports, security improvements

---

Thank you for contributing to Perplex Edge! Your contributions help make sports betting analytics better for everyone. 🎯

## 📞 Contact

For questions about contributing:
- **GitHub Issues**: https://github.com/your-org/perplex-edge/issues
- **Discord**: https://discord.gg/perplex-edge
- **Email**: contribute@perplex-edge.com
