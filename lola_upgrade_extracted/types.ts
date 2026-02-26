export enum ViewState {
  HOME = 'HOME',
  PIPELINE = 'PIPELINE',
  RESULTS = 'RESULTS',
  PROJECTS = 'PROJECTS',
  TEAM = 'TEAM',
  SETTINGS = 'SETTINGS'
}

export type AspectRatio = '1:1' | '9:16' | '16:9' | '4:3' | '3:4' | '4:5';

export interface GeneratedAsset {
  id: string;
  url: string;
  type: 'image' | 'video';
  aspectRatio: AspectRatio;
  createdAt: number;
  prompt: string;
  status: 'completed' | 'generating' | 'failed';
  projectId?: string; // Link asset to a project
}

export interface Project {
  id: string;
  name: string;
  assetCount: number;
  lastEdited: number;
  color: string;
}

export interface ProjectTemplate {
  id: string;
  title: string;
  description: string;
  thumbnail: string;
  icon: string;
  tags: { label: string; color: string }[];
}

export interface PipelineState {
  prompt: string;
  aspectRatio: AspectRatio;
  status: 'idle' | 'running' | 'completed' | 'failed';
  result?: string;
  error?: string;
}

export interface NodeData {
  id: string;
  type: 'input' | 'model' | 'output';
  label: string;
  icon: string;
  x: number;
  y: number;
}