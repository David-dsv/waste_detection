/**
 * Redux Slice pour détections.
 */

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getDetections, detectImage } from '../services/api';

// Thunks asynchrones
export const fetchDetections = createAsyncThunk(
  'detections/fetch',
  async (params) => {
    const data = await getDetections(params);
    return data;
  }
);

export const uploadImage = createAsyncThunk(
  'detections/upload',
  async (formData) => {
    const data = await detectImage(formData);
    return data;
  }
);

const detectionsSlice = createSlice({
  name: 'detections',
  initialState: {
    list: [],
    currentDetection: null,
    total: 0,
    loading: false,
    error: null,
  },
  reducers: {
    clearCurrentDetection: (state) => {
      state.currentDetection = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch detections
      .addCase(fetchDetections.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDetections.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload.detections;
        state.total = action.payload.total;
      })
      .addCase(fetchDetections.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      // Upload image
      .addCase(uploadImage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(uploadImage.fulfilled, (state, action) => {
        state.loading = false;
        state.currentDetection = action.payload;
        // Ajouter à la liste
        state.list.unshift(action.payload);
      })
      .addCase(uploadImage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export const { clearCurrentDetection } = detectionsSlice.actions;
export default detectionsSlice.reducer;
